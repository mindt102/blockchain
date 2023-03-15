import utils
from blockchain import Blockchain, blockchain
from datastructure import VarInt
from protocols.BlockMessage import BlockMessage
from protocols.InvItem import InvItem
from database import get_block_by_hash


class GetDataMessage:
    command = b"getdata"
    __logger = utils.get_logger(__name__)

    def __init__(self, items: list[InvItem]) -> None:
        self.__items = items
        self.__count = VarInt(len(items))

    def get_items(self) -> list:
        return self.__items

    def serialize(self) -> bytes:
        return self.__count.serialize() + b''.join([item.serialize() for item in self.__items])

    @classmethod
    def parse(cls, stream: bytes) -> tuple['GetDataMessage', bytes]:
        count, stream = VarInt.parse(stream)
        items = []
        for _ in range(count.get_value()):
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
                f"Received getdata message from {host} before handshake")
            return
        getdata, _ = cls.parse(payload)
        items = getdata.get_items()
        for item in items:
            if item.get_type() == InvItem.MSG_TX:
                # TODO: Implement
                pass
            elif item.get_type() == InvItem.MSG_BLOCK:
                block_hash = item.get_hash()
                block = get_block_by_hash(block_hash)
                if block:
                    blockmsg = BlockMessage(block)
                    peer.send(blockmsg)
