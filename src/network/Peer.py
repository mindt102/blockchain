import threading


class Peer:
    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port

        self.lock = threading.Lock()
        self.version_sent = False
        self.version_received = False
        self.verack_received = False

    def shookhand(self):
        return self.version_sent and self.version_received and self.verack_received

    def received_version(self):
        self.lock.acquire()
        self.version_received = True
        self.lock.release()

    def received_verack(self):
        self.lock.acquire()
        self.verack_received = True
        self.lock.release()
    
    def sent_version(self):
        self.lock.acquire()
        self.version_sent = True
        self.lock.release()

    def __repr__(self):
        return f"Peer({self.host}:{self.port}, version_sent={self.version_sent}, version_received={self.version_received}, verack_received={self.verack_received})"
