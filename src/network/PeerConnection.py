
from network import NetworkEnvelope
import socket
import utils


class PeerConnection:
    logger = utils.get_logger(__name__)

    def __init__(self, host, port, sock=None):
        self.host = host
        if sock:
            self.sock = sock
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))

    def send(self, message):
        envelope = NetworkEnvelope(message.command, message.serialize())
        self.sock.sendall(envelope.serialize())
        self.logger.info(f"Sent: {message.command} to {self.host}")
        self.close()
            
    def recv(self):
        return self.sock.recv(1024)
    
    def close(self):
        self.sock.close()
