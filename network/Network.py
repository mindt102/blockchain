import queue
import random
import select
import socket
import threading
import time

import utils
from network import NetworkAddress, NetworkEnvelope, Peer
from protocols import AddrMessage, BlockMessage, messages
from Role import Role


class Network(Role):
    '''Provide networking functionality'''
    logger = utils.get_logger(__name__)

    def __init__(self, config):
        self.__id = random.getrandbits(64)
        self.__host = socket.gethostbyname(socket.gethostname())

        self.__port = config["port"] if "port" in config else 8333
        self.__maxpeers = config["max_peers"]
        self.__minpeers = config["min_peers"]
        self.__peer_managing_rate = config["peer_managing_rate"]
        self.__known_nodes = config["known_nodes"] if "known_nodes" in config else [
        ]

        self.__sock = self.__make_server_sock()

        self.__peer_lock = threading.Lock()
        self.__peers: dict[str:Peer] = {}

        self.__init_handlers()

        super().__init__(network=self)

    def run(self):
        self.__discover_known_nodes(self.__known_nodes)
        self.start_peers_manager()
        while True:
            try:
                func, args, kwargs = self.q.get(timeout=self.q_timeout)
                func(*args, **kwargs)
            except queue.Empty:
                self.__idle()
            except KeyboardInterrupt:
                self.logger.info("Closing server")
                break
            except socket.timeout:
                self.logger.info("Timeout")
                break
            except:
                self.logger.exception("Error in network loop")
                break
        self.__sock.close()

    def __idle(self):
        rlist, wlist, xlist = select.select([self.__sock], [], [], 1)
        for sock in rlist:
            if sock is self.__sock:
                client_sock, addr = sock.accept()
                # client_sock.setblocking(0)
                threading.Thread(target=self.__handle_peer,
                                 args=(client_sock, addr)).start()

    # @Role._rpc  # type: ignore
    def start_peers_manager(self):
        threading.Thread(target=self.__manage_peers).start()

    def __discover_known_nodes(self, known_nodes):
        for known_node in known_nodes:
            host, port = known_node
            try:
                host = socket.gethostbyname(host)
            except socket.gaierror:
                self.logger.warning(
                    f"Could not resolve hostname {host}")
                continue
            if host == self.__host:
                continue
            try:
                self.add_peer(host, port)
            except ConnectionRefusedError:
                pass
            except RuntimeError:
                self.logger.warning(
                    f"Could not connect to {host}:{port}")
            except:
                self.logger.exception(
                    f"Could not connect to {host}:{port}")

    def __manage_peers(self):
        while True:
            handshaked_peers = self.get_handshaked_peers()
            if len(handshaked_peers) < self.__minpeers:
                self.broadcast_addr()
            else:
                miner = self.get_miner()
                if not miner.get_network_status():
                    miner.set_network_status(True)
                    self.logger.info(
                        f"Network is ready. Connected to {len(handshaked_peers)} peers")
            # TODO: Check if peer is alive

            time.sleep(self.__peer_managing_rate)

    # @ Role._rpc  # type: ignore
    def broadcast_new_block(self, block, excludes=[]):
        '''Broadcast a new block to all peers'''
        blockmsg = BlockMessage(block)
        self.__broadcast(blockmsg, excludes)

    # @ Role._rpc  # type: ignore
    def broadcast_addr(self):
        network_address = NetworkAddress(ip=self.__host, port=self.__port)
        addrmsg = AddrMessage([network_address])
        self.__broadcast(addrmsg)

    @ Role._rpc  # type: ignore
    def broadcast(self, message, excludes=[]):
        '''Broadcast a message to all peers'''
        self.__broadcast(message, excludes)

    def __broadcast(self, message, excludes=[]):
        self.logger.info(
            f"Broadcasting {message.command}, excludes: {excludes}")

        for peer in self.get_peers().values():
            if peer.get_host() not in excludes and peer.is_handshake_done():
                peer.send(message)

    def __init_handlers(self):
        self.__handlers = {}
        for message in messages:
            self.__handlers[message.command] = message.handler

    def __make_server_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.__host, self.__port))
        sock.listen(self.__maxpeers)

        self.logger.info(f"Listening on {self.__host}:{self.__port}")
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
        '''Add a peer to the list of peers'''
        if host == self.get_host():
            raise ValueError("Cannot connect to self")
        peer = self.get_peer(host)
        if peer:
            if not peer.is_version_sent():
                self.logger.debug(
                    f"Send version to added peer {host}:{port}")
                peer.send_version(self.__id, self.__host, self.__port)
        else:
            if len(self.__peers) == self.__maxpeers:
                self.logger.warning("Reached max peers")
                return
            self.__peer_lock.acquire()
            peer = Peer(host, port)
            self.__peers[host] = peer
            self.__peer_lock.release()
            peer.send_version(self.__id, self.__host, self.__port)

        return self.__peers[host]

    def get_peer(self, host) -> Peer:
        '''Get a peer from the list of peers'''
        if host in self.__peers:
            return self.__peers[host]
        else:
            return None

    def get_peers(self):
        return self.__peers.copy()

    def get_id(self):
        return self.__id

    def get_host(self):
        return self.__host

    def get_port(self):
        return self.__port

    def get_handshaked_peers(self):
        return [peer for peer in self.get_peers().values()
                if peer.is_handshake_done()]
