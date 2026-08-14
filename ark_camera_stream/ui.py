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
        settings = context.scene.arkitcam
        streaming = session.is_streaming()

        self._draw_status(layout.box(), streaming)

        layout.separator()
        layout.prop_search(settings, "target_camera", context.scene, "objects", text="Camera")

        layout.separator()
        self._draw_settings(layout.box(), settings)

        layout.separator()
        self._draw_actions(layout.box(), settings)

        layout.separator()
        if streaming:
            layout.operator("arkitcam.stop", text="Stop Streaming", icon="PAUSE")
        else:
            layout.operator("arkitcam.start", text="Start Streaming", icon="PLAY")

    @staticmethod
    def _draw_status(box, streaming):
        stats = session.get_stats()
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

    @staticmethod
    def _draw_settings(box, settings):
        box.label(text="Settings", icon="SETTINGS")
        col = box.column(align=True)
        col.prop(settings, "host")
        col.prop(settings, "port")
        col.separator()
        col.prop(settings, "scale")
        col.prop(settings, "sensor_width_mm")
        col.prop(settings, "smoothing")
        col.separator()
        col.prop(settings, "orientation")
        col.prop(settings, "fit_resolution")

    @staticmethod
    def _draw_actions(box, settings):
        row = box.row(align=True)
        row.label(text="Actions", icon="ACTION")
        row.operator("arkitcam.open_action_editor", text="", icon="ACTION")
        target = session.resolve_target_camera()
        if target is not None and target.animation_data is not None:
            action = target.animation_data.action
            if action is not None:
                box.label(text=f"Current: {action.name}")
        box.prop(settings, "new_action_on_start")
        box.prop(settings, "record")
