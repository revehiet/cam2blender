# Blender + ARKit Camera Stream

Drive a Blender scene camera in **realtime** from an iPhone's ARKit camera
motion over UDP: position, rotation and focal length (zoom).

```
┌──────────────────────────┐            ┌──────────────────────────────────┐
│ iPhone (ARKit)           │  UDP JSON  │ Blender addon                    │
│ ARSession @ 60 Hz        │──────────▶ │ UDP listener thread              │
│ pose + intrinsics + zoom │  ~150 B/pkt│   └─ lock-protected latest slot   │
└──────────────────────────┘            │ bpy.app.timers callback @ 60 Hz  │
                                        │   └─ ARKit→Blender conversion     │
                                        │      → scene camera (location /   │
                                        │        rotation / lens)           │
                                        │      → optional keyframe recording│
                                        └──────────────────────────────────┘
```

## Repository layout

| Path | Purpose |
| --- | --- |
| `ark_camera_stream/` | The Blender addon (zip this folder to install) |
| `ios/ARKitCameraSender/` | Reference iOS sender app (Swift + SwiftUI) |
| `tools/fake_streamer.py` | Synthetic UDP sender to test without an iPhone |
| `ark_camera_stream_1.0.0.zip` | Ready-to-install addon package |
| `project.yml` + `.github/workflows/` | iOS build in the cloud (XcodeGen + GitHub Actions, no Mac needed) |

## Install the addon in Blender

1. **Edit → Preferences → Add-ons → Install…** and choose
   `ark_camera_stream_1.0.0.zip` (already built) — or zip the contents of the
   `ark_camera_stream/` folder yourself.
2. Enable **ARKit Camera Stream**.
3. A panel **ARKit Cam** appears in the 3D Viewport sidebar (press `N`).
4. Allow the port through the Windows firewall (once, admin PowerShell):

   ```powershell
   New-NetFirewallRule -DisplayName "ARKit Camera UDP" -Direction Inbound -Protocol UDP -LocalPort 60400 -Action Allow
   ```

## Quick start

1. In Blender: sidebar → **ARKit Cam** → **Start Streaming**.
   (Defaults: UDP port `60400`, binds `0.0.0.0`; change under
   **Connection Settings**.)
2. On the iPhone: open the sender app, enter the **PC's LAN IP** and port
   `60400`, tap **Start Streaming**.
3. Move the phone — the chosen camera (default: active scene camera) follows
   in realtime. The zoom slider on the phone changes the camera's **Lens**
   value.

Testing without a phone: run `python tools/fake_streamer.py` on the Blender
machine, then press Start in Blender.

## Focal length / zoom

ARKit reports intrinsics (`fx`, `fy`) in pixels with the image resolution.
Blender's Lens is in millimetres, so the addon converts:

```
lens_mm = fx_pixels × zoom × sensor_width_mm / image_width_px
```

- `zoom` comes live from the iPhone app (digital zoom multiplier).
- `sensor_width_mm` is an addon preference (default 36 mm). The **field of
  view is preserved** for any sensor width — the value only rescales the mm
  number, so the default matches a 36 mm film-gate workflow.
- If the app sends no intrinsics, the Lens value is left untouched.

## Coordinate conversion

| | ARKit | Blender |
| --- | --- | --- |
| Handedness / up | right-handed, Y-up | right-handed, Z-up |
| Camera forward | −Z | −Z |
| Quaternion order | (x, y, z, w) | (w, x, y, z) |

Conversion is a single +90° rotation about X: position `(x, y, z) → (x, −z, y)`,
quaternion `q_B = q_axis ⊗ q_ARK`. ARKit sends metres; the **Position Scale**
preference converts to other scene units.

## Wire protocol (v1)

One JSON datagram per frame:

```json
{"v":1,"type":"frame","t":12.3,
 "p":[0.1,1.2,-0.3],"q":[0.0,0.0,0.0,1.0],
 "fx":1300.5,"fy":1300.0,"iw":1920,"ih":1440,"zoom":1.0}
```

`fx/fy/iw/ih/zoom` are optional; `q` is simd order (x, y, z, w).

## Recording

Enable **Record Keyframes** in the panel while streaming. The addon writes
`location`, `rotation_quaternion` and `lens` keyframes mapped to the scene
timeline (frame = start frame + elapsed seconds × scene FPS), so takes can be
rendered later.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| "Waiting for data" forever | Same LAN? Correct PC IP in the app? Firewall rule added? Correct port on both sides? |
| Camera teleports / wrong scale | Adjust **Position Scale** (1.0 = metres) |
| Jittery motion | Raise **Smoothing** (adds slight lag) |
| Lens looks wrong | Check **Sensor Width** preference and app zoom |
| Port already in use | Stop the stream, change the port in preferences |
| App crashes on launch | Info.plist keys missing — see `ios/README.md` |

## Can I stream without building an app?

ARKit only runs inside an iOS app, so *some* app must be on the phone. The
reference app here is ~200 lines and builds for free with a personal Apple ID
(see `ios/README.md`). If you prefer not to build anything:

- **VirtuCamera** — commercial iOS app + Blender plugin that does exactly
  virtual-camera streaming (but no ARKit world anchoring).
- **CamTrackAR** (FXhome) — free AR camera tracker, but exports files rather
  than streaming live over UDP.
- **Live Link Face** (Epic) — face capture only, not the camera transform.

Building the included iOS app **without a Mac** is supported: GitHub Actions
builds the IPA and you sign it on Windows with Sideloadly — see
`ios/README.md` → Route A.
