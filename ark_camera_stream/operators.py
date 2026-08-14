"""Operators that start/stop the UDP stream and open the Action Editor."""

import bpy

from . import session


def _stream_settings(context):
    try:
        return context.scene.arkitcam
    except AttributeError:
        return None


class ARKITCAM_OT_start(bpy.types.Operator):
    bl_idname = "arkitcam.start"
    bl_label = "Start ARKit Stream"
    bl_description = "Listen for ARKit camera packets over UDP and drive the target camera"

    @classmethod
    def poll(cls, context):
        return not session.is_streaming()

    def execute(self, context):
        settings = _stream_settings(context)
        host = settings.host if settings else "0.0.0.0"
        port = settings.port if settings else 60400
        try:
            session.start_stream(host, port)
        except RuntimeError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        return {"FINISHED"}


class ARKITCAM_OT_stop(bpy.types.Operator):
    bl_idname = "arkitcam.stop"
    bl_label = "Stop ARKit Stream"
    bl_description = "Stop the UDP listener and the camera driver"

    @classmethod
    def poll(cls, context):
        return session.is_streaming()

    def execute(self, context):
        session.stop_stream()
        return {"FINISHED"}


class ARKITCAM_OT_open_action_editor(bpy.types.Operator):
    bl_idname = "arkitcam.open_action_editor"
    bl_label = "Open Action Editor"
    bl_description = "Switch the largest 3D viewport area to the Action Editor"

    @classmethod
    def poll(cls, context):
        return context.screen is not None

    def execute(self, context):
        area = _pick_area(context)
        if area is None:
            self.report({"ERROR"}, "No editor area available")
            return {"CANCELLED"}
        try:
            area.type = "DOPE_SHEET"
            space = area.spaces.active
            if hasattr(space, "ui_mode"):
                space.ui_mode = "ACTION"
        except Exception as exc:
            self.report({"ERROR"}, f"Could not open Action Editor: {exc}")
            return {"CANCELLED"}
        return {"FINISHED"}


def _pick_area(context):
    """Prefer the largest 3D viewport, otherwise the largest area."""
    largest = None
    largest_size = -1
    largest_3d = None
    largest_3d_size = -1
    for area in context.screen.areas:
        size = area.width * area.height
        if size > largest_size:
            largest = area
            largest_size = size
        if area.type == "VIEW_3D" and size > largest_3d_size:
            largest_3d = area
            largest_3d_size = size
    return largest_3d if largest_3d is not None else largest
