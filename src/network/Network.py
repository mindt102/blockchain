import random
import select
import socket
import threading
import queue
from Role import Role

import utils
import protocols
from network import Peer, NetworkEnvelope


class Network(Role):
    logger = utils.get_logger(__name__)

    def __init__(self, server_host, server_port, maxpeers, node_id=None):
        self.id = node_id if node_id else random.getrandbits(64)
        self.host = socket.gethostbyname(server_host)
        self.port = server_port
        self.maxpeers = maxpeers

        self.sock = self.__make_server_sock()

        self.peer_lock = threading.Lock()
        self.peers = {}

        self.__init_handlers()

        super().__init__()

    def run(self):
        while True:
            try:
                func, args, kwargs = self.q.get(timeout=self.q_timeout)
                func(*args, **kwargs)
            except queue.Empty:
                # self.logger.info("Idling")
                self.__idle()
            except KeyboardInterrupt:
                self.logger.info("Closing server")
                break
            except socket.timeout:
                self.logger.info("Timeout")
                break
            except:
                self.logger.exception("Error accepting connection")
                break
        self.sock.close()

    def __idle(self):
        rlist, wlist, xlist = select.select([self.sock], [], [], 1)
        for sock in rlist:
            if sock is self.sock:
                client_sock, addr = sock.accept()
                self.logger.info(f"Accepted connection from {addr}")
                client_sock.setblocking(0)
                threading.Thread(target=self.__handle_peer,
                                 args=(client_sock, addr)).start()

    @Role._rpc  # type: ignore
    def discover_peers(self, known_nodes):
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
                peer = self.add_peer(host, port)
                peer.send_version(self.id, self.host, self.port)
            except KeyboardInterrupt:
                raise
            except ConnectionRefusedError:
                pass
            except:
                self.logger.exception(f"Could not connect to {host}:{port}")

    def __init_handlers(self):
        self.__handlers = {}
        for message in protocols.messages:
            self.__handlers[message.command] = message.handler

    def __make_server_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(self.maxpeers)

        self.logger.info(f"Listening on {self.host}:{self.port}")
        return sock

    def __handle_message(self, host, data):
        message = NetworkEnvelope.parse(data)
        self.logger.info(f"Recv: {message.command} from {host}")
        if message.command in self.__handlers:
            self.__handlers[message.command](self, host, message.payload)
        else:
            self.logger.info(f"Unknown command: {message.command}")

    def __handle_peer(self, client_sock, addr):
        host, port = addr
        # peer_connection = PeerConnection(host, port, client_sock)

        try:
            data = client_sock.recv(1024)
            if data:
                self.__handle_message(host, data)

        except KeyboardInterrupt:
            raise
        except:
            self.logger.exception(f"Error handling peer {host}:{port}")
        client_sock.close()

    def add_peer(self, host, port) -> Peer:
        if host not in self.peers:
            if len(self.peers) == self.maxpeers:
                raise RuntimeError("Reached max peers")
            self.peer_lock.acquire()
            self.peers[host] = Peer(host, port)
            self.peer_lock.release()

        return self.peers[host]
