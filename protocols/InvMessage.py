import utils
from datastructure import VarInt
from protocols.GetDataMessage import GetDataMessage
from protocols.InvItem import InvItem


class InvMessage:
    command = b"inv"
    __logger = utils.get_logger(__name__)

    def __init__(self, items: list) -> None:
        self.__items = items
        self.__count = VarInt(len(items))

    def serialize(self) -> bytes:
        return self.__count.value + b''.join([item.serialize() for item in self.__items])

    @classmethod
    def parse(cls, stream: bytes) -> tuple['InvMessage', bytes]:
        count, stream = VarInt.parse(stream)
        items = []
        for _ in range(count.__value):
            item, stream = InvItem.parse(stream)
            items.append(item)
        return cls(items), stream

    def __repr__(self) -> str:
        return f"InvMessage(items={self.__items})"

    def get_items(self) -> list:
        return self.__items

    @classmethod
    def handler(cls, network, host, payload):
        peer = network.get_peer(host)
        if not (peer and peer.is_handshake_done()):
            cls.__logger.warning(
                f"Received inv message from {host} before handshake")
            return
        inv, _ = cls.parse(payload)
        filtered_items = []
        miner = network.get_miner()
        blockchain = network.get_blockchain()
        for item in inv.get_items():
            if item.get_type() == InvItem.MSG_TX:  # Transaction
                # Check if transaction is in mempool or in blockchain
                tx = miner.get_tx_by_hash(
                    item.get_hash()) or blockchain.get_tx_by_hash(item.get_hash())
                if tx:
                    continue

                filtered_items.append(item)
            elif item.get_type() == InvItem.MSG_BLOCK:  # Block
                # Check if blockchain already has the block
                block = blockchain.get_block_by_hash(item.get_hash())
                if block:
                    continue
                filtered_items.append(item)

                # TODO: Remove this
                miner.receive_new_block()
            else:
                cls.__logger.warning(
                    f"Received inv message with unknown type {item.type}")
        getdata = GetDataMessage(filtered_items)
        peer.send(getdata)
