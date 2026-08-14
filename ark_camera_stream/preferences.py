"""Addon preferences."""

import bpy


class ARKitCameraPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

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

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, "host")
        col.prop(self, "port")
        layout.separator()
        layout.prop(self, "scale")
        layout.prop(self, "sensor_width_mm")
        layout.prop(self, "smoothing")
