import math
import utils
from blockchain import Blockchain
from datastructure import VarInt
from Miner import Miner
from protocols.GetDataMessage import GetDataMessage
from protocols.InvItem import InvItem


class InvMessage:
    command = b"inv"
    __logger = utils.get_logger(__name__)

    def __init__(self, items: list) -> None:
        self.__items = items
        self.__count = VarInt(len(items))

    def serialize(self) -> bytes:
        return self.__count.serialize() + b''.join([item.serialize() for item in self.__items])

    @classmethod
    def parse(cls, stream: bytes) -> tuple['InvMessage', bytes]:
        count, stream = VarInt.parse(stream)
        items = []
        for _ in range(count.get_value()):
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
        cls.__logger.info(inv)
        filtered_items = []
        miner: Miner = network.get_miner()
        blockchain: Blockchain = network.get_blockchain()

        # Filter out items that are already in mempool or blockchain
        for item in inv.get_items():
            if network.is_requested(item.get_hash()):
                continue
            if item.get_type() == InvItem.MSG_TX:  # Transaction
                #         # Check if transaction is in mempool or in blockchain
                tx = miner.get_tx_by_hash(
                    item.get_hash()) or blockchain.get_tx_by_hash(item.get_hash())
                if tx:
                    continue

            elif item.get_type() == InvItem.MSG_BLOCK:  # Block
                # Check if blockchain already has the block
                header = blockchain.get_header_by_hash(item.get_hash())
                if header:
                    continue

            else:
                cls.__logger.warning(
                    f"Received inv message with unknown type {item.type}")
                continue
            filtered_items.append(item)
            network.add_requested(item.get_hash())

        if not filtered_items:
            cls.__logger.debug("No new items to request")
            return

        if len(filtered_items) == 1:
            getdata = GetDataMessage(filtered_items)
            peer.send(getdata)
        else:
            # Split filtered items into multiple getdata messages
            from network import Peer
            peers: Peer = network.get_peers()
            peer_count = len(peers)
            chunk_size = math.ceil(len(filtered_items) // peer_count)

            for i, receiver in enumerate(peers.values()):
                start = i * chunk_size
                end = min((i + 1) * chunk_size, len(filtered_items))
                data = filtered_items[start:end]
                getdata = GetDataMessage(data)
                cls.__logger.debug(
                    f"#{i} Sending {getdata} to {receiver.get_host()}: {receiver.get_port()}")
                receiver.send(getdata)
