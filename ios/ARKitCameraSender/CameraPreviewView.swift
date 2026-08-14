import SwiftUI
import RealityKit
import UIKit

/// Live ARKit camera preview (RealityKit ARView in `.ar` mode).
///
/// Supports pinch-to-zoom: the gesture scales the digital zoom factor that
/// is sent to Blender (the phone's camera itself has no zoom API, so the
/// preview stays optically unzoomed).
struct CameraPreviewView: UIViewRepresentable {
    let streamer: CameraStreamer

    func makeCoordinator() -> Coordinator {
        Coordinator(streamer: streamer)
    }

    func makeUIView(context: Context) -> ARView {
        let arView = ARView(frame: .zero)
        streamer.attach(to: arView)

        let pinch = UIPinchGestureRecognizer(
            target: context.coordinator,
            action: #selector(Coordinator.handlePinch(_:))
        )
        pinch.delegate = context.coordinator
        arView.addGestureRecognizer(pinch)
        context.coordinator.pinchGesture = pinch
        return arView
    }

    func updateUIView(_ uiView: ARView, context: Context) {}

    final class Coordinator: NSObject, UIGestureRecognizerDelegate {
        let streamer: CameraStreamer
        var pinchGesture: UIPinchGestureRecognizer?
        private var pinchStartZoom: Double = 1.0

        init(streamer: CameraStreamer) {
            self.streamer = streamer
        }

        @objc func handlePinch(_ sender: UIPinchGestureRecognizer) {
            switch sender.state {
            case .began:
                pinchStartZoom = streamer.zoom
            case .changed:
                let newZoom = pinchStartZoom * Double(sender.scale)
                streamer.zoom = min(max(newZoom, 0.1), 10.0)
            default:
                break
            }
        }

        func gestureRecognizer(
            _ gestureRecognizer: UIGestureRecognizer,
            shouldRecognizeSimultaneouslyWith otherGestureRecognizer: UIGestureRecognizer
        ) -> Bool {
            true
        }
    }
}
