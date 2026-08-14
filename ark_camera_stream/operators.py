"""Operators that start and stop the UDP stream."""

import bpy

from . import session


def _addon_preferences(context):
    addon = context.preferences.addons.get(__package__)
    return addon.preferences if addon is not None else None


class ARKITCAM_OT_start(bpy.types.Operator):
    bl_idname = "arkitcam.start"
    bl_label = "Start ARKit Stream"
    bl_description = "Listen for ARKit camera packets over UDP and drive the target camera"

    @classmethod
    def poll(cls, context):
        return not session.is_streaming()

    def execute(self, context):
        prefs = _addon_preferences(context)
        host = prefs.host if prefs else "0.0.0.0"
        port = prefs.port if prefs else 60400
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
