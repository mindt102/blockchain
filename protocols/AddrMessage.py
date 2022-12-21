import utils
from datastructure import VarInt
from network import NetworkAddress


class AddrMessage:
    command = b"addr"
    __logger = utils.get_logger(__name__)

    def __init__(self, addresses: list['NetworkAddress']):
        self.__count = VarInt(len(addresses))
        self.__addresses = addresses

    def serialize(self) -> bytes:
        return self.__count.serialize() + b''.join([addr.serialize() for addr in self.__addresses])

    @classmethod
    def parse(cls, stream: bytes) -> tuple['AddrMessage', bytes]:
        count, stream = VarInt.parse(stream)
        addresses = []
        for _ in range(count.get_value()):
            addr, stream = NetworkAddress.parse(stream)
            addresses.append(addr)
        return cls(addresses), stream

    def __repr__(self):
        return f"Addr(count={self.__count}, addresses={self.__addresses})"

    @classmethod
    def handler(cls, network, host, payload):
        cls.__logger.info(f"Addr received from {host}")
        from network import Peer
        peer: Peer = network.get_peer(host)
        if not peer.is_active():
            peer.send_version()
        if not (peer and peer.is_handshake_done()):
            cls.__logger.warning(
                f"Received message from {host} before handshake")
            return
        # if peer.is_addr_relayed():
        #     return
        addr, _ = cls.parse(payload)

        if addr.get_count() == 1:
            address = addr.get_addresses()[0]
            address_host = address.get_host()
            if address_host == host:
                network.broadcast(
                    addr, excludes=[host, address_host])
                return
            # peer.relayed_addr()

        for address in addr.get_addresses():
            if address.get_host() == network.get_host():
                continue
            network.add_peer(address.get_host(), address.get_port())

    def get_count(self):
        return self.__count.get_value()

    def get_addresses(self):
        return self.__addresses
