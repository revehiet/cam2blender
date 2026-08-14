import SwiftUI

struct ContentView: View {
    @StateObject private var streamer = CameraStreamer()
    @State private var host = "192.168.68.56"
    @State private var port = "60400"
    @State private var isFullScreenPreview = false

    var body: some View {
        Group {
            if isFullScreenPreview {
                fullScreenPreview
            } else {
                formView
            }
        }
    }

    private var formView: some View {
        NavigationView {
            Form {
                Section {
                    ZStack(alignment: .topTrailing) {
                        CameraPreviewView(streamer: streamer)
                            .frame(height: 240)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                        Button {
                            isFullScreenPreview = true
                        } label: {
                            Image(systemName: "arrow.up.left.and.arrow.down.right")
                                .padding(8)
                                .background(Color.black.opacity(0.4))
                                .foregroundColor(.white)
                                .clipShape(Circle())
                        }
                        .padding(8)
                    }
                    .listRowInsets(EdgeInsets())
                }
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
                        Slider(value: Binding(
                            get: { streamer.zoom },
                            set: { streamer.zoom = min(max($0, 0.1), 10.0) }
                        ), in: 0.1...10.0)
                    }
                    Text("Zoom multiplies the focal length sent to Blender, which changes the scene camera's Lens value. The preview stays unzoomed.")
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

    private var fullScreenPreview: some View {
        ZStack(alignment: .bottom) {
            CameraPreviewView(streamer: streamer)
                .ignoresSafeArea()
            VStack {
                HStack {
                    Label(streamer.trackingText,
                          systemImage: streamer.isStreaming
                              ? "dot.radiowaves.left.and.right"
                              : "pause.circle")
                        .font(.caption)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 6)
                        .background(Color.black.opacity(0.4))
                        .foregroundColor(.white)
                        .clipShape(Capsule())
                    Spacer()
                    Button {
                        isFullScreenPreview = false
                    } label: {
                        Image(systemName: "arrow.down.right.and.arrow.up.left")
                            .padding(10)
                            .background(Color.black.opacity(0.4))
                            .foregroundColor(.white)
                            .clipShape(Circle())
                    }
                }
                .padding()
                Spacer()
                HStack(spacing: 12) {
                    Image(systemName: "minus.magnifyingglass")
                        .foregroundColor(.white)
                    Slider(value: Binding(
                        get: { streamer.zoom },
                        set: { streamer.zoom = min(max($0, 0.1), 10.0) }
                    ), in: 0.1...10.0)
                    Image(systemName: "plus.magnifyingglass")
                        .foregroundColor(.white)
                    Text(String(format: "%.2fx", streamer.zoom))
                        .font(.caption)
                        .foregroundColor(.white)
                        .frame(width: 48)
                }
                .padding(.horizontal)
                .padding(.vertical, 10)
                .background(Color.black.opacity(0.4))
            }
        }
        .statusBarHidden(true)
    }
}
