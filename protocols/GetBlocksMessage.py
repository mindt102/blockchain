from blockchain import Blockchain
from protocols import InvItem, InvMessage
import utils
from datastructure import VarInt


class GetBlocksMessage:
    command = b"getblocks"
    __logger = utils.get_logger(__name__)

    def __init__(self, block_locator_hashes: list) -> None:
        self.__block_locator_hashes = block_locator_hashes
        self.__count = VarInt(len(block_locator_hashes))

    def get_block_locator_hashes(self) -> list[bytes]:
        return self.__block_locator_hashes

    def serialize(self) -> bytes:
        return self.__count.serialize() + b''.join(self.__block_locator_hashes)

    @classmethod
    def parse(cls, stream: bytes) -> tuple['GetBlocksMessage', bytes]:
        count, stream = VarInt.parse(stream)
        block_locator_hashes = []
        for _ in range(count.get_value()):
            block_locator_hash, stream = stream[:32], stream[32:]
            block_locator_hashes.append(block_locator_hash)
        return cls(block_locator_hashes), stream

    def __repr__(self) -> str:
        return f"GetBlocksMessage(block_locator_hashes={self.__block_locator_hashes})"

    @classmethod
    def handler(cls, network, host, payload):
        peer = network.get_peer(host)
        if not (peer and peer.is_handshake_done()):
            cls.__logger.warning(
                f"Received inv message from {host} before handshake")
            return
        getblocks, _ = cls.parse(payload)

        blockchain: Blockchain = network.get_blockchain()
        block_locator_hashes = getblocks.get_block_locator_hashes()
        common_block_hash = blockchain.locate_common_block_hash(
            block_locator_hashes)
        shared_block_hashes = blockchain.share_blocks_from_hash(
            common_block_hash)
        inv_message = InvMessage(
            [InvItem(InvItem.MSG_BLOCK, block_hash) for block_hash in shared_block_hashes])
        peer.send(inv_message)
