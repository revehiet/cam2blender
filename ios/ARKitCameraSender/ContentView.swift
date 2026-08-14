import SwiftUI

struct ContentView: View {
    @StateObject private var streamer = CameraStreamer()
    @State private var host = "192.168.0.10"
    @State private var port = "60400"

    var body: some View {
        NavigationView {
            Form {
                Section("Connection (Blender PC)") {
                    TextField("IP address", text: $host)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                    TextField("UDP port", text: $port)
                        .keyboardType(.numberPad)
                }

                Section("Lens / Zoom") {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(String(format: "Digital zoom: %.2f", streamer.zoom) + "x")
                        Slider(value: $streamer.zoom, in: 0.1...10.0)
                    }
                    Text("Zoom multiplies the focal length sent to Blender, which changes the scene camera's Lens value.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Section("Status") {
                    Label(streamer.trackingText,
                          systemImage: streamer.isStreaming
                              ? "dot.radiowaves.left.and.right"
                              : "pause.circle")
                }

                Section {
                    Button(streamer.isStreaming ? "Stop Streaming" : "Start Streaming") {
                        if streamer.isStreaming {
                            streamer.stop()
                        } else {
                            guard let portValue = UInt16(port), !host.isEmpty else {
                                streamer.trackingText = "Enter a valid IP and port"
                                return
                            }
                            streamer.start(host: host, port: portValue)
                        }
                    }
                    .frame(maxWidth: .infinity)
                }
            }
            .navigationTitle("ARKit Camera Sender")
        }
    }
}
