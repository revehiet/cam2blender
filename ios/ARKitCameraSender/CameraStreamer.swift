import Foundation
import Network
import ARKit
import QuartzCore

/// Streams ARKit camera pose and lens data to the Blender addon over UDP.
///
/// Wire protocol v1 (JSON, UTF-8, one datagram per frame):
/// {
///   "v": 1, "type": "frame", "t": <seconds since session start>,
///   "p": [x, y, z],             // camera position, metres, ARKit axes (Y-up)
///   "q": [x, y, z, w],          // orientation quaternion, simd order (x, y, z, w)
///   "fx": <float>, "fy": <float>,   // intrinsics focal length in pixels
///   "iw": <width>, "ih": <height>,  // image resolution in pixels
///   "zoom": <float>                 // digital zoom multiplier
/// }
final class CameraStreamer: NSObject, ObservableObject {
    @Published private(set) var isStreaming = false
    @Published var trackingText = "Idle"

    /// Digital zoom: multiplies the focal length sent to Blender.
    @Published var zoom: Double = 1.0 {
        didSet { zoom = min(max(zoom, 0.1), 10.0) }
    }

    private let session = ARSession()
    private var connection: NWConnection?
    private var host = ""
    private var port: UInt16 = 0
    private var lastSent: CFTimeInterval = 0

    // MARK: - Lifecycle

    func start(host: String, port: UInt16) {
        stop()
        self.host = host
        self.port = port
        lastSent = 0
        trackingText = "Connecting..."

        let configuration = ARWorldTrackingConfiguration()
        session.delegate = self
        session.run(configuration)

        let connection = NWConnection(
            host: NWEndpoint.Host(host),
            port: NWEndpoint.Port(rawValue: port)!,
            using: .udp
        )
        connection.stateUpdateHandler = { [weak self] state in
            DispatchQueue.main.async {
                switch state {
                case .ready:
                    self?.isStreaming = true
                case .failed(let error):
                    self?.isStreaming = false
                    self?.trackingText = "Network error: \(error.localizedDescription)"
                default:
                    break
                }
            }
        }
        connection.start(queue: .global(qos: .userInitiated))
        self.connection = connection
    }

    func stop() {
        connection?.cancel()
        connection = nil
        session.pause()
        isStreaming = false
        trackingText = "Stopped"
    }

    // MARK: - ARSessionDelegate

    func session(_ session: ARSession, didUpdate frame: ARFrame) {
        guard let connection = connection, isStreaming else { return }

        // Throttle to ~60 packets/second (UDP drops are handled fine by Blender).
        let now = CACurrentMediaTime()
        guard now - lastSent >= 1.0 / 60.0 else { return }
        lastSent = now

        let transform = frame.camera.transform
        let p = SIMD3<Float>(
            transform.columns.3.x,
            transform.columns.3.y,
            transform.columns.3.z
        )
        let q = simd_quaternion(transform)

        let intrinsics = frame.camera.intrinsics
        let fx = intrinsics.columns.0.x
        let fy = intrinsics.columns.1.y
        let width = Float(frame.camera.imageResolution.width)
        let height = Float(frame.camera.imageResolution.height)

        let payload: [String: Any] = [
            "v": 1,
            "type": "frame",
            "t": frame.timestamp,
            "p": [p.x, p.y, p.z],
            "q": [q.vector.x, q.vector.y, q.vector.z, q.vector.w],
            "fx": fx,
            "fy": fy,
            "iw": width,
            "ih": height,
            "zoom": zoom,
        ]

        guard let data = try? JSONSerialization.data(withJSONObject: payload) else {
            return
        }
        connection.send(content: data, completion: .contentProcessed { _ in })
    }

    func session(_ session: ARSession, cameraDidChangeTrackingState camera: ARCamera) {
        let text: String
        switch camera.trackingState {
        case .normal:
            text = "Tracking: normal"
        case .notAvailable:
            text = "Tracking: unavailable"
        case .limited(let reason):
            text = "Tracking limited: \(reason)"
        }
        DispatchQueue.main.async { [weak self] in
            self?.trackingText = text
        }
    }

    func session(_ session: ARSession, didFailWithError error: Error) {
        DispatchQueue.main.async { [weak self] in
            self?.trackingText = "ARSession error: \(error.localizedDescription)"
            self?.stop()
        }
    }
}
