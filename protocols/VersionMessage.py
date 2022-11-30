import struct
import time
import random
import utils
from protocols.VerAckMessage import VerAckMessage
from network import NetworkAddress
from datastructure import VarStr


class VersionMessage():
    command = b'version'
    __logger = utils.get_logger(__name__)

    def __init__(self, nonce, timestamp=None,
                 addr_recv=None, addr_from=None, user_agent='/ucoin:0.1/', start_height=0):
        self.__timestamp = timestamp if timestamp else int(time.time())
        self.__addr_recv = addr_recv
        self.__addr_from = addr_from
        self.__nonce = nonce if nonce else random.getrandbits(64)

        self.__user_agent = user_agent if isinstance(
            user_agent, VarStr) else VarStr(user_agent)

        self.__start_height = start_height

    def set_addr_recv(self, addr_recv: NetworkAddress):
        self.__addr_recv = addr_recv

    def set_addr_from(self, addr_from: NetworkAddress):
        self.__addr_from = addr_from

    def serialize(self):
        return self.__timestamp.to_bytes(8, 'little') + self.__addr_recv.serialize() + self.__addr_from.serialize() + self.__nonce.to_bytes(8, 'little') + self.__user_agent.serialize() + self.__start_height.to_bytes(4, 'little')

    @classmethod
    def parse(cls, stream):
        timestamp = int.from_bytes(stream[:8], 'little')
        stream = stream[8:]
        addr_recv, stream = NetworkAddress.parse(stream)
        addr_from, stream = NetworkAddress.parse(stream)
        nonce = int.from_bytes(stream[:8], 'little')
        stream = stream[8:]
        user_agent, stream = VarStr.parse(stream)
        start_height = int.from_bytes(stream[:4], 'little')
        stream = stream[4:]
        return cls(nonce, timestamp, addr_recv, addr_from, user_agent, start_height)

    @classmethod
    def handler(cls, network, host, payload):
        version = cls.parse(payload)
        remote_host = version.__addr_from.get_host()
        remote_port = version.__addr_from.get_port()
        remote_nodeid = version.__nonce

        if remote_host != host:
            cls.__logger.warning(f'Host mismatch: {host} != {remote_host}')
            return
        if remote_nodeid == network.get_id():
            raise RuntimeError("Connected to self")

        peer = network.get_peer(host) or network.add_peer(
            remote_host, remote_port)
        if peer:
            if peer.is_version_received():
                cls.__logger.warning(f'Already received version from {host}')
                return
            peer.received_version()
            peer.send(VerAckMessage())
            if not peer.is_version_sent():
                peer.send_version(network.get_id(),
                                  network.get_host(), network.get_port())

    def __repr__(self):
        return f'VersionMessage(version={self.__version}, services={self.__services}, timestamp={self.__timestamp}, addr_recv={self.__addr_recv}, addr_from={self.__addr_from}, nonce={self.__nonce}, user_agent={self.__user_agent}, start_height={self.__start_height}, relay={self.__relay})'
