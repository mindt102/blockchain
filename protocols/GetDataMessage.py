from typing import Self
import utils
from datastructure import VarInt
from protocols.InvItem import InvItem


class GetDataMessage:
    command = b"getdata"
    __logger = utils.get_logger(__name__)

    def __init__(self, items: list) -> None:
        self.__items = items
        self.__count = VarInt(len(items))

    def serialize(self) -> bytes:
        return self.__count.value + b''.join([item.serialize() for item in self.__items])

    @classmethod
    def parse(cls, stream: bytes) -> tuple[Self, bytes]:
        count, stream = VarInt.parse(stream)
        items = []
        for _ in range(count.integer):
            item, stream = InvItem.parse(stream)
            items.append(item)
        return cls(items), stream

    def __repr__(self) -> str:
        return f"GetDataMessage(items={self.__items})"

    @classmethod
    def handler(cls, network, host, payload):
        peer = network.get_peer(host)
        if not (peer and peer.is_handshake_done()):
            cls.__logger.warning(
                f"Received inv message from {host} before handshake")
            return
        getdata, _ = cls.parse(payload)
        cls.__logger.info(getdata)
