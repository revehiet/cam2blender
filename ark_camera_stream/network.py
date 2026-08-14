"""Background UDP listener thread.

Blender's ``bpy`` module must never be touched from this thread: parsing is
pure Python and the datagram callback only stores results in a
lock-protected slot (see ``session.py``).
"""

import socket
import threading


class UDPCameraListener:
    def __init__(self, host, port, on_datagram, max_bytes=65535):
        self.host = host
        self.port = int(port)
        self.on_datagram = on_datagram
        self.max_bytes = max_bytes
        self._socket = None
        self._thread = None
        self._stop = threading.Event()

    @property
    def is_running(self):
        return self._thread is not None and self._thread.is_alive()

    def start(self):
        """Bind the socket (raises OSError if unavailable) and launch the
        receive thread."""
        if self.is_running:
            return
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
        except OSError:
            sock.close()
            raise
        sock.settimeout(0.5)
        self._socket = sock
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run, name="ARKitCamUDP", daemon=True
        )
        self._thread.start()

    def _run(self):
        while not self._stop.is_set():
            try:
                data, _addr = self._socket.recvfrom(self.max_bytes)
            except socket.timeout:
                continue
            except OSError:
                break  # socket closed during shutdown
            if data:
                try:
                    self.on_datagram(data)
                except Exception:
                    # The callback must never kill the receive thread.
                    pass

    def stop(self):
        self._stop.set()
        if self._socket is not None:
            try:
                self._socket.close()
            except OSError:
                pass
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        self._socket = None
        self._thread = None
