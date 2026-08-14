"""User interface: viewport sidebar panel."""

import time

import bpy

from . import session


class ARKITCAM_PT_panel(bpy.types.Panel):
    bl_label = "ARKit Camera"
    bl_idname = "ARKITCAM_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ARKit Cam"

    def draw(self, context):
        layout = self.layout
        props = context.scene.arkitcam
        streaming = session.is_streaming()
        stats = session.get_stats()

        box = layout.box()
        col = box.column(align=True)
        if streaming:
            col.label(text="Status: streaming", icon="PLAY")
            elapsed = max(time.time() - stats.get("started", 0.0), 1e-6)
            packets = stats.get("packets", 0)
            col.label(text=f"Packets: {packets} ({packets / elapsed:.0f}/s)")
            col.label(text=f"Malformed: {stats.get('malformed', 0)}")
            last = stats.get("last_packet", 0.0)
            age = (time.time() - last) if last else None
            if age is None or age > 1.0:
                col.label(text="Waiting for data from iOS...", icon="INFO")
        else:
            col.label(text="Status: stopped", icon="PAUSE")

        layout.separator()
        layout.prop_search(props, "target_camera", context.scene, "objects", text="Camera")
        layout.prop(props, "record")

        layout.separator()
        if streaming:
            layout.operator("arkitcam.stop", text="Stop Streaming", icon="PAUSE")
        else:
            layout.operator("arkitcam.start", text="Start Streaming", icon="PLAY")
        layout.operator(
            "preferences.addon_show",
            text="Connection Settings",
            icon="PREFERENCES",
        ).module = __package__
