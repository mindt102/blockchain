import socket
import threading

from network import NetworkAddress, NetworkEnvelope
import protocols
import utils


class Peer:
    logger = utils.get_logger(__name__)

    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port

        self.version_sent = False
        self.version_received = False
        self.verack_received = False

    def is_handshake_done(self):
        return self.version_sent and self.version_received and self.verack_received

    def received_version(self):
        self.version_received = True

    def received_verack(self):
        self.verack_received = True

    def sent_version(self):
        self.version_sent = True

    def send(self, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))

        envelope = NetworkEnvelope(message.command, message.serialize())
        sock.sendall(envelope.serialize())
        self.logger.info(f"Sent: {message.command} to {self.host}")

        sock.close()

    def send_version(self, server_id, server_host, server_port):
        version = protocols.VersionMessage(nonce=server_id)
        version.set_addr_recv(NetworkAddress(ip=self.host, port=self.port))
        version.set_addr_from(NetworkAddress(ip=server_host, port=server_port))
        try:
            self.send(version)
            self.sent_version()
        except ConnectionRefusedError:
            self.logger.warning(
                f"Connection to {server_host}:{server_port} refused")
        except:
            self.logger.exception(
                f"Fail to send version to {server_host}:{server_port}")
            return

    def __repr__(self):
        return f"Peer({self.host}:{self.port}, version_sent={self.version_sent}, version_received={self.version_received}, verack_received={self.verack_received})"
