"""ARKit Camera Stream - Blender addon.

Receives ARKit camera pose + lens data from an iOS app over UDP and drives
the scene camera in realtime. Compatible with the stable bpy API used by
Blender 4.x and 5.x.
"""

import bpy

from . import conversion, network, operators, preferences, protocol, session, ui  # noqa: F401

bl_info = {
    "name": "ARKit Camera Stream",
    "description": (
        "Drive the scene camera in realtime from an iOS ARKit app over UDP "
        "(position, rotation and focal length)."
    ),
    "author": "ARKit Camera Stream",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "3D Viewport > Sidebar > ARKit Cam",
    "category": "3D View",
}


class ARKITCAM_SceneProps(bpy.types.PropertyGroup):
    bl_idname = "ARKITCAM_SceneProps"

    target_camera: bpy.props.PointerProperty(
        name="Target Camera",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == "CAMERA",
        description="Camera driven by the stream (empty = active scene camera)",
    )
    record: bpy.props.BoolProperty(
        name="Record Keyframes",
        description="Write location, rotation and lens keyframes while streaming",
        default=False,
    )


_CLASSES = (
    ARKITCAM_SceneProps,
    preferences.ARKitCameraPreferences,
    operators.ARKITCAM_OT_start,
    operators.ARKITCAM_OT_stop,
    ui.ARKITCAM_PT_panel,
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.arkitcam = bpy.props.PointerProperty(type=ARKITCAM_SceneProps)
    bpy.app.handlers.load_pre.append(_stop_on_load)


def unregister():
    session.stop_stream()
    try:
        bpy.app.handlers.load_pre.remove(_stop_on_load)
    except ValueError:
        pass
    if hasattr(bpy.types.Scene, "arkitcam"):
        del bpy.types.Scene.arkitcam
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)


def _stop_on_load(_dummy):
    session.stop_stream()
