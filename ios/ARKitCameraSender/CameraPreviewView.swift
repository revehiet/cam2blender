import SwiftUI
import RealityKit

/// Live ARKit camera preview (RealityKit ARView in `.ar` mode).
struct CameraPreviewView: UIViewRepresentable {
    let streamer: CameraStreamer

    func makeUIView(context: Context) -> ARView {
        let arView = ARView(frame: .zero)
        streamer.attach(to: arView)
        return arView
    }

    func updateUIView(_ uiView: ARView, context: Context) {}
}
