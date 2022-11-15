import random
import socket
import threading

import utils
import protocols
from network import Peer, PeerConnection, NetworkEnvelope, NetworkAddress


class Node:
    logger = utils.get_logger(__name__)
    
    def __init__(self, server_host, server_port, maxpeers, node_id=None, known_nodes=[]):
        self.id = node_id if node_id else random.getrandbits(64)
        self.host = socket.gethostbyname(server_host)
        self.port = server_port
        self.maxpeers = maxpeers

        self.peer_lock = threading.Lock()
        self.peers = {}

        self.__init_handlers()

        if not known_nodes:
            raise RuntimeError("Must provide at least one known node")

        self.server_thread = threading.Thread(target=self.__run)
        self.server_thread.start()

        self.__discover_peers(known_nodes)

    def __init_handlers(self):
        self.__handlers = {}
        for message in protocols.messages:
            self.__add_handler(message.command, message.handle)

    def __add_handler(self, command, handler):
        self.__handlers[command] = handler

    def __make_server_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(20)
        sock.bind((self.host, self.port))
        sock.listen(5)
        self.logger.info(f"Listening on {self.host}:{self.port}")
        return sock

    def __run(self):
        server_sock = self.__make_server_sock()
        while True:
            try:
                client_sock, addr = server_sock.accept()
                client_sock.settimeout(None)
                threading.Thread(target=self.__handle_peer, args=(client_sock,addr)).start()
            except KeyboardInterrupt:
                self.logger.info("Closing server")
                break
            except socket.timeout:
                self.logger.info("Timeout")
                break
            except:
                self.logger.exception("Error accepting connection")
                break
        server_sock.close()

    def __discover_peers(self, known_nodes):
        for known_node in known_nodes:
            host, port = known_node
            
            try:
                host = socket.gethostbyname(host)
            except socket.gaierror:
                self.logger.warning(f"Could not resolve hostname {host}")
                continue

            if host == self.host:
                continue

            try:
                self.send_version(host, port)
            except KeyboardInterrupt:
                raise
            except ConnectionRefusedError:
                pass
            except:
                self.logger.exception(f"Could not connect to {host}:{port}")

    def __handle_message(self, host, data):
        message = NetworkEnvelope.parse(data)
        self.logger.info(f"Recv: {message.command} from {host}")	
        if message.command in self.__handlers:
            self.__handlers[message.command](self, host, message.payload)
        else:
            self.logger.info(f"Unknown command: {message.command}")

    def __handle_peer(self, client_sock, addr):
        host, port = addr
        peer_connection = PeerConnection(host, port, client_sock)

        try:
            data = peer_connection.recv()
            if data:
                self.__handle_message(host, data)

        except KeyboardInterrupt:
            raise
        except:
            self.logger.exception(f"Error handling peer {host}:{port}")
        peer_connection.close()

    def send_version(self, host, port):
        if host in self.peers:
            peer = self.peers[host]
            if peer.version_sent:
                return True
        elif len(self.peers) == self.maxpeers:
            return False
        else:
            peer = Peer(host, port)
            self.peers[host] = peer
        version = protocols.VersionMessage(nonce=self.id)
        version.addr_recv = NetworkAddress(ip=host, port=port)
        version.addr_from = NetworkAddress(ip=self.host, port=self.port)
        try:
            self.connect_and_send(host, port, version)
            self.peers[host].sent_version()
        except ConnectionRefusedError:
            pass
        except:
            self.logger.exception(f"Fail to send version to {host}:{port}")
            return

    def connect_and_send(self, host, port, message):
        peer_connection = PeerConnection(host, port)
        peer_connection.send(message)

    def add_peer(self, host, port):
        if host in self.peers:
            return
        if len(self.peers) == self.maxpeers:
            return
        self.peer_lock.acquire()
        self.peers[host] = Peer(host, port)
        self.peer_lock.release()

    def get_peer(self, peerid):
        return self.peers[peerid]

    def remove_peer(self, peerid):
        if peerid in self.peers:
            del self.peers[peerid]
