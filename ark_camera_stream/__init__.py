"""ARKit Camera Stream - Blender addon.

Receives ARKit camera pose + lens data from an iOS app over UDP and drives
the scene camera in realtime. Compatible with the stable bpy API used by
Blender 4.x and 5.x.
"""

import bpy

from . import conversion, network, operators, protocol, session, settings, ui  # noqa: F401

bl_info = {
    "name": "ARKit Camera Stream",
    "description": (
        "Drive the scene camera in realtime from an iOS ARKit app over UDP "
        "(position, rotation and focal length)."
    ),
    "author": "ARKit Camera Stream",
    "version": (1, 1, 1),
    "blender": (4, 0, 0),
    "location": "3D Viewport > Sidebar > ARKit Cam",
    "category": "3D View",
}

_CLASSES = (
    settings.ARKitCameraSettings,
    operators.ARKITCAM_OT_start,
    operators.ARKITCAM_OT_stop,
    operators.ARKITCAM_OT_open_action_editor,
    ui.ARKITCAM_PT_panel,
    ui.ARKITCAM_PT_settings,
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.arkitcam = bpy.props.PointerProperty(type=settings.ARKitCameraSettings)
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
