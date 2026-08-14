"""Streaming session: shared state, UDP callback and the main-thread applier.

Threading contract:
  * ``network.UDPCameraListener`` runs in a background thread and only
    writes to ``_latest_frame`` / ``_stats`` under ``_slot_lock``.
  * ``_apply_tick`` runs on Blender's main thread via ``bpy.app.timers``
    and is the only place that mutates scene objects.
"""

import threading
import time

import bpy

from . import conversion, network, protocol

_TICK = 1.0 / 60.0

_listener = None
_timer = None

_slot_lock = threading.Lock()
_latest_frame = None

_stats = {"started": 0.0, "packets": 0, "malformed": 0, "last_packet": 0.0}

_smooth_pos = None
_smooth_quat = None

_record_start_t = None
_record_start_frame = 1
_last_record_frame = None


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #


def is_streaming():
    return _listener is not None and _listener.is_running


def get_stats():
    return dict(_stats)


def resolve_target_camera():
    """Return the camera object to drive (panel choice, else scene camera)."""
    scene = bpy.context.scene
    obj = None
    try:
        obj = scene.arkitcam.target_camera
    except AttributeError:
        pass
    if obj is None or obj.type != "CAMERA":
        obj = scene.camera
    return obj if (obj is not None and obj.type == "CAMERA") else None


def start_stream(host, port):
    global _listener, _timer

    if is_streaming():
        return

    _reset_smoothing()
    _reset_recording()
    _stats.update(started=time.time(), packets=0, malformed=0, last_packet=0.0)

    listener = network.UDPCameraListener(host or "0.0.0.0", port, _on_datagram)
    try:
        listener.start()
    except OSError as exc:
        raise RuntimeError(f"Could not bind UDP {host}:{port} - {exc}") from exc

    _listener = listener
    _timer = bpy.app.timers.register(_apply_tick, first_interval=_TICK)


def stop_stream():
    global _listener, _timer

    if _timer is not None:
        try:
            bpy.app.timers.unregister(_timer)
        except ValueError:
            pass
        _timer = None

    if _listener is not None:
        _listener.stop()
        _listener = None

    _reset_smoothing()
    _reset_recording()


# --------------------------------------------------------------------------- #
# Background-thread side
# --------------------------------------------------------------------------- #


def _on_datagram(data):
    now = time.time()
    packet = protocol.parse_frame(data, arrival_time=now)
    global _latest_frame
    with _slot_lock:
        _stats["packets"] += 1
        _stats["last_packet"] = now
        if packet is None:
            _stats["malformed"] += 1
            return
        _latest_frame = packet


# --------------------------------------------------------------------------- #
# Main-thread side
# --------------------------------------------------------------------------- #


def _get_preferences():
    addon = bpy.context.preferences.addons.get(__package__)
    return addon.preferences if addon is not None else None


def _apply_tick():
    if not is_streaming():
        return None  # stop the timer
    try:
        _apply_latest()
    except Exception:
        # A bad frame or a temporary context problem must never kill the
        # timer; the next tick simply tries again.
        pass
    return _TICK


def _apply_latest():
    global _smooth_pos, _smooth_quat

    prefs = _get_preferences()
    scale = prefs.scale if prefs else 1.0
    sensor_mm = prefs.sensor_width_mm if prefs else 36.0
    smoothing = prefs.smoothing if prefs else 0.0

    target = resolve_target_camera()
    if target is None:
        return
    if target.rotation_mode != "QUATERNION":
        target.rotation_mode = "QUATERNION"

    with _slot_lock:
        frame = _latest_frame
    if frame is None:
        return

    pos = conversion.position_to_blender(frame.position) * scale
    quat = conversion.quaternion_to_blender(frame.quaternion)

    if smoothing > 0.0 and _smooth_pos is not None:
        _smooth_pos = _smooth_pos.lerp(pos, smoothing)
        _smooth_quat = _smooth_quat.slerp(quat, smoothing)
    else:
        _smooth_pos = pos
        _smooth_quat = quat

    target.location = _smooth_pos
    target.rotation_quaternion = _smooth_quat

    lens = conversion.focal_length_mm(
        frame.fx, frame.image_width, frame.zoom, sensor_mm
    )
    if lens is not None and lens > 0.0:
        target.data.lens = lens

    _record_frame(target, frame, lens)


def _record_frame(target, frame, lens):
    global _record_start_t, _record_start_frame, _last_record_frame

    scene = bpy.context.scene
    try:
        recording = bool(scene.arkitcam.record)
    except AttributeError:
        recording = False

    if not recording:
        _record_start_t = None
        _last_record_frame = None
        return

    if _record_start_t is None:
        _record_start_t = frame.timestamp
        _record_start_frame = scene.frame_current
        _last_record_frame = None

    fps = scene.render.fps / scene.render.fps_base
    frame_number = _record_start_frame + int(
        round((frame.timestamp - _record_start_t) * fps)
    )
    if frame_number == _last_record_frame:
        return
    _last_record_frame = frame_number

    target.keyframe_insert(data_path="location", frame=frame_number)
    target.keyframe_insert(data_path="rotation_quaternion", frame=frame_number)
    if lens is not None:
        target.data.keyframe_insert(data_path="lens", frame=frame_number)


# --------------------------------------------------------------------------- #
# State helpers
# --------------------------------------------------------------------------- #


def _reset_smoothing():
    global _smooth_pos, _smooth_quat
    _smooth_pos = None
    _smooth_quat = None


def _reset_recording():
    global _record_start_t, _record_start_frame, _last_record_frame
    _record_start_t = None
    _record_start_frame = 1
    _last_record_frame = None
