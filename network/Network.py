import queue
import random
import select
import socket
import threading
import time
from blockchain import blockchain
import database

import utils
from network import NetworkAddress, NetworkEnvelope, Peer
from protocols import AddrMessage, BlockMessage, GetBlocksMessage, InvItem, TransactionMessage, messages, GetDataMessage
from Role import Role


class Network(Role):
    '''Provide networking functionality'''
    __logger = utils.get_logger(__name__)

    def __init__(self, config):
        self.__id = random.getrandbits(64)
        self.__host = socket.gethostbyname(socket.gethostname())

        self.__port = config["port"] if "port" in config else 8333
        self.__maxpeers = config["max_peers"]
        self.__minpeers = config["min_peers"]
        self.__network_managing_rate = config["peer_managing_rate"]
        self.__chain_syncing_rate = config["chain_syncing_rate"]
        self.__known_nodes = config["known_nodes"] if "known_nodes" in config else [
        ]

        self.__peer_lock = threading.Lock()
        self.__peers: dict[str:Peer] = {}

        self.__init_handlers()
        self.__blockchain_sync_started = False

        self.__max_peer_start_height = 0

        self.__is_ready = False

        self.__item_lock = threading.Lock()
        self.__requested_items = set()
        super().__init__()

    def run(self):
        self.__sock = self.__make_server_sock()
        self.__discover_known_nodes(self.__known_nodes)
        self.__start_network_manager()
        while self.active():
            try:
                func, args, kwargs = self.q.get(timeout=self.q_timeout)
                func(*args, **kwargs)
            except queue.Empty:
                self.__idle()
            except KeyboardInterrupt:
                self.__logger.info("Closing server")
                break
            except socket.timeout:
                self.__logger.info("Timeout")
                break
            except:
                self.__logger.exception("Error in network loop")
                break
        self.__sock.close()

    def __idle(self):
        rlist, wlist, xlist = select.select([self.__sock], [], [], 1)
        for sock in rlist:
            if sock is self.__sock:
                client_sock, addr = sock.accept()
                threading.Thread(target=self.__handle_peer,
                                 args=(client_sock, addr)).start()

    def __start_network_manager(self):
        threading.Thread(target=self.__manage_network, daemon=True).start()

    def __discover_known_nodes(self, known_nodes):
        for known_node in known_nodes:
            host, port = known_node
            try:
                host = socket.gethostbyname(host)
            except socket.gaierror:
                self.__logger.warning(
                    f"Could not resolve hostname {host}")
                continue
            if host == self.__host:
                continue
            try:
                self.add_peer(host, port)
            except ConnectionRefusedError:
                pass
            except RuntimeError:
                self.__logger.warning(
                    f"Could not connect to {host}:{port}")
            except:
                self.__logger.exception(
                    f"Could not connect to {host}:{port}")

    def __sync_local_blockchain(self):
        block_locator_hashes = blockchain.get_block_locator_hashes()
        getblocks_msg = GetBlocksMessage(block_locator_hashes)
        self.broadcast(getblocks_msg)

    def __manage_network(self):
        while True:
            handshaked_peers = self.get_handshaked_peers()
            if len(handshaked_peers) < self.__minpeers:
                self.broadcast_addr()
            else:
                # Network is ready
                if not self.is_ready():
                    self.set_ready()
                    self.__logger.info(
                        f"Network is ready. Connected to {len(handshaked_peers)} peers")

                # Start blockchain sync if not started
                if not self.__blockchain_sync_started:
                    self.__sync_local_blockchain()
                    self.__blockchain_sync_started = True
                    self.__logger.info(
                        f"Syncing blockchain with max peer height {self.__max_peer_start_height}")
                    self.__chain_sync_timer = 0

                if not blockchain.is_ready():
                    height = database.get_max_height()
                    if height >= self.__max_peer_start_height:
                        self.__logger.info(
                            f"Blockchain is up to date. Height: {height}")
                        blockchain.set_ready()
                    else:
                        self.__chain_sync_timer += self.__network_managing_rate
                        if self.__chain_sync_timer >= self.__chain_syncing_rate:
                            self.__sync_local_blockchain()
                            self.__chain_sync_timer = 0

            time.sleep(self.__network_managing_rate)

    def broadcast_new_block(self, block, excludes=[]):
        '''Broadcast a new block to all peers'''
        blockmsg = BlockMessage(block)
        self.broadcast(blockmsg, excludes)

    def broadcast_new_tx(self, tx, excludes=[]):
        '''Broadcast a new transaction to all peers'''
        txmsg = TransactionMessage(tx)
        self.broadcast(txmsg, excludes)

    # @ Role._rpc  # type: ignore
    def broadcast_addr(self):
        network_address = NetworkAddress(ip=self.__host, port=self.__port)
        addrmsg = AddrMessage([network_address])
        self.broadcast(addrmsg)

    def request_parent(self, parent_hash, peer):
        item = InvItem(InvItem.MSG_BLOCK, parent_hash)
        getdata_msg = GetDataMessage([item])
        if peer and peer in self.get_peers() and self.get_peers[peer].is_handshake_done():
            self.get_peers[peer].send(getdata_msg)
        else:
            self.broadcast(getdata_msg)
    # @ Role._rpc  # type: ignore
    # def broadcast(self, message, excludes=[]):
    #     '''Broadcast a message to all peers'''
    #     self.broadcast(message, excludes)

    def broadcast(self, message, excludes=[]):
        self.__logger.info(
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

        self.__logger.info(f"Listening on port {self.__port}...")
        return sock

    def __handle_message(self, host, data):
        message = NetworkEnvelope.parse(data)
        if not message:
            self.__logger.warning(f"Could not parse message from {host}")
            return
        # self.__logger.info(f"Recv: {message.command} from {host}")
        if message.command in self.__handlers:
            self.__handlers[message.command](self, host, message.payload)
        else:
            self.__logger.info(f"Unknown command: {message.command}")

    def __handle_peer(self, client_sock, addr):
        host, port = addr
        try:
            data = b''
            while self.active():
                buffer = client_sock.recv(1024)
                if not buffer:
                    break
                data += buffer
                if len(buffer) < 1024:
                    break
            if data:
                self.__handle_message(host, data)
        except KeyboardInterrupt:
            raise
        except:
            self.__logger.exception(f"Error handling peer {host}:{port}")
        client_sock.close()

    def add_peer(self, host, port) -> Peer:
        '''Add a peer to the list of peers'''
        if host == self.get_host():
            raise ValueError("Cannot connect to self")
        peer = self.get_peer(host)
        # height = self.get_blockchain().get_height()
        height = database.get_max_height()
        if peer:
            if not peer.is_version_sent():
                peer.send_version(self.__id, self.__host, self.__port, height)
        else:
            if len(self.__peers) == self.__maxpeers:
                self.__logger.warning("Reached max peers")
                return
            self.__peer_lock.acquire()
            peer = Peer(host, port)
            self.__peers[host] = peer
            self.__peer_lock.release()
            peer.send_version(self.__id, self.__host,
                              self.__port, height=height)

        return self.__peers[host]

    def get_peer(self, host) -> Peer:
        '''Get a peer from the list of peers'''
        if host in self.__peers:
            return self.__peers[host]
        else:
            return None

    def get_peers(self) -> dict[str, Peer]:
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

    def set_max_peer_start_height(self, height):
        '''Set the maximum height of peers during startup'''
        if height > self.__max_peer_start_height:
            self.__max_peer_start_height = height

    def is_ready(self):
        '''Check if the network is ready'''
        return self.__is_ready

    def set_ready(self):
        '''Set the network ready status'''
        self.__is_ready = True

    def is_requested(self, item_hash: bytes):
        '''Check if an item is requested'''
        self.__item_lock.acquire()
        result = item_hash in self.__requested_items
        self.__item_lock.release()
        return result

    def add_requested(self, item_hash: bytes):
        '''Add an item to requested items'''
        self.__item_lock.acquire()
        self.__requested_items.add(item_hash)
        self.__item_lock.release()

    def remove_requested(self, item_hash: bytes):
        '''Remove an item from requested items'''
        self.__item_lock.acquire()
        if item_hash in self.__requested_items:
            self.__requested_items.remove(item_hash)
        self.__item_lock.release()
