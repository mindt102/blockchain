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
                 addr_recv=NetworkAddress(), addr_from=NetworkAddress(), user_agent='/ucoin:0.1/', start_height=0, relay=1):
        self.version = version
        self.services = services
        if not timestamp:
            self.timestamp = int(time.time())
        else:
            self.timestamp = timestamp
        self.addr_recv = addr_recv
        self.addr_from = addr_from
        if not nonce:
            self.nonce = random.getrandbits(64)
        else:
            self.nonce = nonce

        if isinstance(user_agent, VarStr):
            self.user_agent = user_agent
        else:
            self.user_agent = VarStr(user_agent)
        self.start_height = start_height
        self.relay = relay

    def serialize(self):
        return (struct.pack('<LQQ', self.version, self.services, self.timestamp)
                + self.addr_recv.serialize()
                + self.addr_from.serialize()
                + struct.pack('<Q', self.nonce)
                + self.user_agent.value
                + struct.pack('<L?', self.start_height, self.relay)
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
    def handler(cls, node, host, payload):
        version = cls.parse(payload)
        remote_host = version.addr_from.get_ip_string()
        remote_port = version.addr_from.port
        remote_nodeid = version.nonce

        if remote_host != host:
            cls.__logger.warning(f'Host mismatch: {host} != {remote_host}')
            return
        if remote_nodeid == node.id:
            raise RuntimeError("Connected to self")

        if host in node.peers:
            if node.peers[host].version_received:
                cls.__logger.warning(f'Already received version from {host}')
                return

        peer = node.add_peer(remote_host, remote_port)
        peer.received_version()
        peer.send(VerAckMessage())
        if not peer.version_sent:
            peer.send_version(node.id, node.host, node.port)

    def __repr__(self):
        return f'VersionMessage(version={self.version}, services={self.services}, timestamp={self.timestamp}, addr_recv={self.addr_recv}, addr_from={self.addr_from}, nonce={self.nonce}, user_agent={self.user_agent}, start_height={self.start_height}, relay={self.relay})'
