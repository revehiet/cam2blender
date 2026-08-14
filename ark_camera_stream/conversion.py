"""ARKit <-> Blender coordinate conversions.

ARKit uses a right-handed, Y-up coordinate system with the camera looking
down its local -Z axis. Blender uses a right-handed, Z-up system where the
camera also looks down its local -Z axis.

Mapping ARKit -> Blender is a single +90 degree rotation about X:

    position:   (x, y, z)_ARK -> (x, -z, y)_Blender
    quaternion: q_Blender = q_axis @ q_ARKit

Quaternion component order differs between the two worlds: ARKit/simd uses
(x, y, z, w), Blender uses (w, x, y, z).
"""

import math

from mathutils import Quaternion, Vector

# +90 degrees about the X axis: maps Y-up to Z-up (and Z to -Y).
_AXIS_FIX = Quaternion(
    (math.cos(math.pi / 4.0), math.sin(math.pi / 4.0), 0.0, 0.0)
)


def position_to_blender(position):
    """ARKit (x, y, z) metres -> Blender Vector (x, -z, y)."""
    x, y, z = position
    return Vector((x, -z, y))


def quaternion_to_blender(quaternion):
    """ARKit (x, y, z, w) -> Blender Quaternion."""
    x, y, z, w = quaternion
    return _AXIS_FIX @ Quaternion((w, x, y, z))


def focal_length_mm(fx_pixels, image_width_pixels, zoom, sensor_width_mm):
    """Convert a pixel-space focal length to millimetres.

    The resulting value preserves the horizontal field of view for a Blender
    camera whose sensor is ``sensor_width_mm`` wide and whose image is
    ``image_width_pixels`` pixels wide:

        FOV_h = 2 * atan(image_width_pixels / (2 * fx_pixels * zoom))
        lens  = fx_pixels * zoom * sensor_width_mm / image_width_pixels
    """
    if not fx_pixels or not image_width_pixels:
        return None
    fx = float(fx_pixels)
    width = float(image_width_pixels)
    if fx <= 0.0 or width <= 0.0:
        return None
    return fx * float(zoom) * float(sensor_width_mm) / width


def apply_roll(quaternion, degrees):
    """Rotate the camera around its own viewing axis (local Z)."""
    if not degrees:
        return quaternion
    half = math.radians(degrees) / 2.0
    roll = Quaternion((math.cos(half), 0.0, 0.0, math.sin(half)))
    return quaternion @ roll
