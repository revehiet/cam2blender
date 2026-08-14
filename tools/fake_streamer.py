"""Synthetic ARKit streamer for testing the addon without an iPhone.

Usage:
    python tools/fake_streamer.py [host] [port]

Sends a camera orbiting at ~1.2 m radius, always looking at the world
origin, with a fixed focal length, at ~60 Hz. Run it on the same machine
as Blender (default host 127.0.0.1) or from any machine on the LAN.
"""

import json
import math
import socket
import sys
import time


def normalize(v):
    n = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    return (v[0] / n, v[1] / n, v[2] / n)


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def quat_between(a, b):
    """Shortest-arc quaternion rotating direction ``a`` onto ``b``.

    Returns ARKit/simd component order (x, y, z, w).
    """
    a = normalize(a)
    b = normalize(b)
    d = dot(a, b)
    if d > 0.99999:
        return (0.0, 0.0, 0.0, 1.0)
    if d < -0.99999:
        axis = cross(a, (0.0, 1.0, 0.0))
        if dot(axis, axis) < 1e-6:
            axis = (1.0, 0.0, 0.0)
        axis = normalize(axis)
        return (axis[0], axis[1], axis[2], 0.0)
    v = cross(a, b)
    w = 1.0 + d
    q = (v[0], v[1], v[2], w)
    return normalize(q)


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 60400

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    target = (host, port)

    t0 = time.perf_counter()
    print(f"Streaming synthetic ARKit camera to {host}:{port} (Ctrl+C to stop)")
    try:
        while True:
            t = time.perf_counter() - t0
            angle = t * 0.5  # radians per second
            radius = 1.2
            x = radius * math.cos(angle)
            y = 0.5 + 0.2 * math.sin(t)
            z = radius * math.sin(angle)

            # Camera looks at the origin from ARKit camera space (forward is -Z).
            forward = normalize((-x, -y, -z))
            q = quat_between((0.0, 0.0, -1.0), forward)

            packet = {
                "v": 1,
                "type": "frame",
                "t": t,
                "p": [x, y, z],
                "q": list(q),
                "fx": 1300.0,
                "fy": 1300.0,
                "iw": 1920.0,
                "ih": 1440.0,
                "zoom": 1.0,
            }
            sock.sendto(json.dumps(packet).encode("utf-8"), target)
            time.sleep(1.0 / 60.0)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
