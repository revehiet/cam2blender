"""Wire protocol for the ARKit Camera Stream addon.

The iOS app sends versioned JSON packets over UDP, one datagram per frame.
All values are in ARKit-native convention and are converted to Blender
conventions by ``conversion.py``:

    {"v":1,"type":"frame","t":12.3,
     "p":[x,y,z],              # position, metres, ARKit axes (right-handed, Y-up)
     "q":[x,y,z,w],            # orientation quaternion, simd order (x, y, z, w)
     "fx":1300.5,"fy":1300.0,  # intrinsics focal length in pixels (optional)
     "iw":1920,"ih":1440,      # image resolution in pixels (optional)
     "zoom":1.0}               # digital zoom multiplier (optional, default 1.0)
"""

import json

PROTOCOL_VERSION = 1
TYPE_FRAME = "frame"


class FramePacket:
    """A single parsed camera frame from the iOS app."""

    __slots__ = (
        "timestamp",
        "position",
        "quaternion",
        "fx",
        "fy",
        "image_width",
        "image_height",
        "zoom",
        "arrival_time",
    )

    def __init__(
        self,
        timestamp,
        position,
        quaternion,
        fx=None,
        fy=None,
        image_width=None,
        image_height=None,
        zoom=1.0,
        arrival_time=0.0,
    ):
        self.timestamp = float(timestamp)
        self.position = tuple(float(v) for v in position)
        self.quaternion = tuple(float(v) for v in quaternion)  # x, y, z, w
        self.fx = None if fx is None else float(fx)
        self.fy = None if fy is None else float(fy)
        self.image_width = None if image_width is None else float(image_width)
        self.image_height = None if image_height is None else float(image_height)
        self.zoom = float(zoom) if zoom else 1.0
        self.arrival_time = float(arrival_time)


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_number_sequence(value, expected_length):
    return (
        isinstance(value, (list, tuple))
        and len(value) == expected_length
        and all(_is_number(v) for v in value)
    )


def _optional_float(obj, key):
    value = obj.get(key)
    if _is_number(value):
        return float(value)
    return None


def parse_frame(data, arrival_time=0.0):
    """Parse a UDP payload into a FramePacket, or return None if invalid."""
    try:
        obj = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
        return None

    if not isinstance(obj, dict):
        return None
    if obj.get("type") != TYPE_FRAME:
        return None
    if obj.get("v") != PROTOCOL_VERSION:
        return None

    p = obj.get("p")
    q = obj.get("q")
    if not _is_number_sequence(p, 3) or not _is_number_sequence(q, 4):
        return None

    try:
        return FramePacket(
            timestamp=obj.get("t", 0.0),
            position=p,
            quaternion=q,
            fx=_optional_float(obj, "fx"),
            fy=_optional_float(obj, "fy"),
            image_width=_optional_float(obj, "iw"),
            image_height=_optional_float(obj, "ih"),
            zoom=_optional_float(obj, "zoom") or 1.0,
            arrival_time=arrival_time,
        )
    except (TypeError, ValueError):
        return None
