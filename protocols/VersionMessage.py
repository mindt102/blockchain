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

    def __init__(self, nonce, version=1, services=1, timestamp=None,
                 addr_recv=None, addr_from=None, user_agent='/ucoin:0.1/', start_height=0, relay=1):
        self.__version = version
        self.__services = services
        if not timestamp:
            self.__timestamp = int(time.time())
        else:
            self.__timestamp = timestamp
        self.__addr_recv = addr_recv
        self.__addr_from = addr_from
        if not nonce:
            self.__nonce = random.getrandbits(64)
        else:
            self.__nonce = nonce

        if isinstance(user_agent, VarStr):
            self.__user_agent = user_agent
        else:
            self.__user_agent = VarStr(user_agent)
        self.__start_height = start_height
        self.__relay = relay

    def set_addr_recv(self, addr_recv: NetworkAddress):
        self.__addr_recv = addr_recv

    def set_addr_from(self, addr_from: NetworkAddress):
        self.__addr_from = addr_from

    def serialize(self):
        return (struct.pack('<LQQ', self.__version, self.__services, self.__timestamp)
                + self.__addr_recv.serialize()
                + self.__addr_from.serialize()
                + struct.pack('<Q', self.__nonce)
                + self.__user_agent.value
                + struct.pack('<L?', self.__start_height, self.__relay)
                )

    @classmethod
    def parse(cls, stream):
        version = struct.unpack('<L', stream[:4])[0]
        services = struct.unpack('<Q', stream[4:12])[0]
        timestamp = struct.unpack('<Q', stream[12:20])[0]
        addr_recv = NetworkAddress.parse(stream[20:46])
        addr_from = NetworkAddress.parse(stream[46:72])
        nonce = struct.unpack('<Q', stream[72:80])[0]

        user_agent, stream = VarStr.parse(stream[80:])

        start_height = struct.unpack(
            '<L', stream[:-1])[0]  # type: ignore
        relay = struct.unpack('?', stream[-1:])[0]
        return cls(nonce, version, services, timestamp, addr_recv, addr_from, user_agent, start_height, relay)

    @classmethod
    def handler(cls, network, host, payload):
        version = cls.parse(payload)
        remote_host = version.__addr_from.get_ip_string()
        remote_port = version.__addr_from.port
        remote_nodeid = version.__nonce

        if remote_host != host:
            cls.__logger.warning(f'Host mismatch: {host} != {remote_host}')
            return
        if remote_nodeid == network.id:
            raise RuntimeError("Connected to self")

        peer = network.get_peer(host)
        if peer:
            if network.get_peer(host).version_received:
                cls.__logger.warning(f'Already received version from {host}')
                return
        else:
            peer = network.add_peer(remote_host, remote_port)
        peer.received_version()
        peer.send(VerAckMessage())
        if not peer.version_sent:
            peer.send_version(network.id, network.host, network.port)

    def __repr__(self):
        return f'VersionMessage(version={self.__version}, services={self.__services}, timestamp={self.__timestamp}, addr_recv={self.__addr_recv}, addr_from={self.__addr_from}, nonce={self.__nonce}, user_agent={self.__user_agent}, start_height={self.__start_height}, relay={self.__relay})'
