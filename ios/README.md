# ARKit Camera Sender (iOS)

Reference iOS app that streams the ARKit camera pose and focal length to the
Blender addon over UDP, ~60 packets/second. For personal use only.

> **On Windows with no Mac?** Use Route A below: GitHub Actions builds the
> IPA in the cloud and Sideloadly signs it on your PC. The Xcode-on-a-Mac
> instructions are kept at the bottom (Route B).

## Requirements

- A way to build: either **GitHub Actions** (Route A — no Mac at all) or a
  **Mac with Xcode 15+** (Route B). iOS apps cannot be compiled on Windows
  directly, so Route A runs the build on a cloud macOS runner instead.
- An iPhone with ARKit world tracking (iPhone 6s/SE or newer).
- iOS 16+ is recommended (Developer Mode requirement below).
- The phone and the Blender PC must be on the **same network**.

## Route A — Build on GitHub Actions, sign with Sideloadly (Windows)

The repo already contains everything needed: `project.yml` (project
definition for XcodeGen) and `.github/workflows/build-ios.yml`.

1. Push this folder to a GitHub repository. Create an empty repo on
   github.com first (public is fine — there are no secrets in the code, and
   public repos get free build minutes):

   ```powershell
   cd "c:\Users\revehiet\blender ar"
   git init
   git config user.name "Your Name"
   git config user.email "you@example.com"
   git add .
   git commit -m "ARKit camera stream project"
   git branch -M main
   git remote add origin https://github.com/<you>/<repo>.git
   git push -u origin main
   ```

2. GitHub → your repo → **Actions** → **Build iOS IPA** → **Run workflow**.
   A macOS runner generates the Xcode project with XcodeGen and builds an
   unsigned IPA in ~5 minutes.
3. Download the **ARKitCameraSender-unsigned** artifact and extract the `.ipa`.
4. On Windows, install **iTunes from Apple** (provides the iPhone USB
   drivers) and **Sideloadly** (sideloadly.io). AltStore is an alternative.
5. On the iPhone enable **Developer Mode**: Settings → Privacy & Security →
   Developer Mode → on → restart (iOS 16+). Connect via USB and trust the PC.
6. In Sideloadly: drag the `.ipa` in, sign in with your **free Apple ID**,
   click **Start**. First launch: Settings → General → VPN & Device
   Management → your Apple ID → **Trust**.

Free accounts expire after **7 days** — repeat step 6 to renew (AltServer can
auto-refresh over Wi-Fi while the PC is on). A paid Apple Developer account
(USD 99/year) extends expiry to 1 year.

## Route B — Create the Xcode project

1. Xcode → **File → New → Project…** → **iOS → App**.
2. Product name: `ARKitCameraSender`, Interface: **SwiftUI**, Language: **Swift**.
3. Replace the generated `ContentView.swift` with the one from this folder and
   add `CameraStreamer.swift` and `ARKitCameraSenderApp.swift` to the target
   (drag the files into the project navigator, tick "Copy items if needed").
4. Set the **deployment target** to iOS 15 or later.

## Info.plist keys (mandatory)

Both routes ship a static `ios/Info.plist` with these keys (Route A wires it
up through `project.yml`; for Route B copy the file into your Xcode project
or add the keys in the target's Info tab):

| Key | Value |
| --- | --- |
| Privacy - Camera Usage Description | Streams camera pose to Blender over your local network |
| Privacy - Local Network Usage Description | Connects to the Blender PC on your local network |

Without these the app **crashes** (camera) or **silently cannot send**
(local network, iOS 14+).

## Route B — Build and install with Xcode (no App Store)

1. Xcode → **Settings → Accounts** → sign in with your personal **Apple ID**
   (free account is enough).
2. Select the project → target → **Signing & Capabilities**:
   - Tick **Automatically manage signing**.
   - Team: **your personal team**.
   - Change the Bundle Identifier to something unique, e.g.
     `com.yourname.arkitcamerasender`.
3. Connect the iPhone via USB, select it as the run destination.
4. On the iPhone: **Settings → Privacy & Security → Developer Mode** → enable
   and restart the phone (iOS 16+).
5. Press **Run (⌘R)**. The first time, trust the developer certificate on the
   phone: **Settings → General → VPN & Device Management → your Apple ID → Trust**.

### Expiry with a free account

Free Apple ID apps **expire after 7 days**. To refresh: plug the phone into the
Mac and press Run again in Xcode. A paid Apple Developer account (USD 99/year)
extends this to 1 year and removes the app-count limits (free accounts can only
sign a handful of apps at once).

## Using the app

1. Start the Blender addon ("Start Streaming") on the PC.
2. Allow the inbound UDP port through the PC firewall (see the root README).
3. Enter the **Blender PC's LAN IP** (find it with `ipconfig` on Windows,
   e.g. `192.168.68.56`) and port `60400`.
4. Tap **Start Streaming** — the live camera preview appears at the top of
   the app — move the phone and the Blender camera follows.
5. Zoom with the **pinch gesture** on the preview (or the slider) — it scales
   the focal length sent to Blender (the preview stays optically unzoomed).
   Tap the expand button on the preview for a full-screen camera view.

### If the camera doesn't move

- On first start the app asks for **Camera** and **Local Network** access —
  accept both prompts.
- If the local-network prompt never appeared: Settings → Privacy & Security →
  Local Network → switch the app ON. If it isn't listed there, delete and
  reinstall the app (privacy state resets on reinstall).
- The IP field must be the **PC's LAN IP**, not the router's address.
- The PC firewall must allow inbound UDP 60400 (see the root README).
- In Blender's panel the **Packets** counter should climb to ~60/s while
  streaming.
