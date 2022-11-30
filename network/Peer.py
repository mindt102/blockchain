import socket
import threading

from network import NetworkAddress, NetworkEnvelope
import protocols
import utils


class Peer:
    logger = utils.get_logger(__name__)

    def __init__(self, host, port) -> None:
        self.__host = host
        self.__port = port

        self.__status = {
            "version_sent": False,
            "version_received": False,
            "verack_received": False,
        }

    def is_handshake_done(self):
        return self.is_version_sent() and self.is_version_received() and self.is_verack_received()

    def is_version_sent(self):
        return self.__status["version_sent"]

    def is_version_received(self):
        return self.__status["version_received"]

    def is_verack_received(self):
        return self.__status["verack_received"]

    def received_version(self):
        self.__status["version_received"] = True

    def received_verack(self):
        self.__status["verack_received"] = True

    def sent_version(self):
        self.__status["version_sent"] = True

    def send(self, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.__host, self.__port))

        envelope = NetworkEnvelope(message.command, message.serialize())
        sock.sendall(envelope.serialize())
        self.logger.info(f"Sent: {message.command} to {self.__host}")

        sock.close()

    def send_version(self, server_id, server_host, server_port):
        version = protocols.VersionMessage(nonce=server_id)
        version.set_addr_recv(NetworkAddress(ip=self.__host, port=self.__port))
        version.set_addr_from(NetworkAddress(ip=server_host, port=server_port))
        try:
            self.send(version)
            self.sent_version()
        except ConnectionRefusedError:
            self.logger.warning(
                f"Connection to {self.get_host()}:{self.get_port()} refused")
        except:
            self.logger.exception(
                f"Fail to send version to {self.get_host()}:{self.get_port()}")
            return

    def __repr__(self):
        return f"Peer({self.__host}:{self.__port}, {self.__status})"

    def get_host(self):
        return self.__host

    def get_port(self):
        return self.__port
