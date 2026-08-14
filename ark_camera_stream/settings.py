"""Stream settings.

All settings live on the scene (``bpy.types.Scene.arkitcam``) and are exposed
in the viewport N-panel, so nothing is hidden in addon preferences.
"""

import bpy


class ARKitCameraSettings(bpy.types.PropertyGroup):
    bl_idname = "ARKITCAM_SceneProps"

    host: bpy.props.StringProperty(
        name="Bind Address",
        description=(
            "Interface to listen on. 0.0.0.0 accepts packets from any "
            "interface (recommended)"
        ),
        default="0.0.0.0",
    )
    port: bpy.props.IntProperty(
        name="UDP Port",
        description="Port the iOS app sends to (must match the app setting)",
        default=60400,
        min=1,
        max=65535,
    )
    scale: bpy.props.FloatProperty(
        name="Position Scale",
        description="Multiplier applied to the received position (ARKit sends metres)",
        default=1.0,
        min=0.0001,
        soft_max=10.0,
    )
    sensor_width_mm: bpy.props.FloatProperty(
        name="Sensor Width (mm)",
        description=(
            "Horizontal sensor size used to convert the iOS focal length "
            "in pixels to millimetres. 36 mm is Blender's default; the "
            "field of view is preserved regardless of this value"
        ),
        default=36.0,
        min=0.1,
        soft_max=70.0,
    )
    smoothing: bpy.props.FloatProperty(
        name="Smoothing",
        description=(
            "Blend factor applied to each new frame (0 = raw data, "
            "higher = smoother but laggier)"
        ),
        default=0.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
    )
    floor_height: bpy.props.FloatProperty(
        name="Floor Height",
        description=(
            "Vertical offset added to the camera position on world Z "
            "(scene units, applied after the position scale)"
        ),
        default=0.0,
        soft_min=-10.0,
        soft_max=10.0,
    )
    roll_offset: bpy.props.FloatProperty(
        name="Roll Offset (deg)",
        description=(
            "Manual rotation around the camera's local Z axis to correct "
            "the orientation if the image appears rolled"
        ),
        default=0.0,
        min=-180.0,
        max=180.0,
    )
    orientation: bpy.props.EnumProperty(
        name="Orientation",
        description=(
            "How the iPhone is held; used to orient the render resolution "
            "to match the camera image"
        ),
        items=[
            ("HORIZONTAL", "Horizontal", "Landscape: resolution matches the sensor image"),
            ("VERTICAL", "Vertical", "Portrait: resolution is swapped for an upright phone"),
        ],
        default="VERTICAL",
    )
    fit_resolution: bpy.props.BoolProperty(
        name="Fit Render Resolution",
        description=(
            "Set the render resolution from the iPhone's image size so the "
            "render aspect ratio matches the camera"
        ),
        default=True,
    )
    new_action_on_start: bpy.props.BoolProperty(
        name="New Action on Start",
        description=(
            "Create and assign a new numbered action to the camera each "
            "time streaming starts"
        ),
        default=True,
    )
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
