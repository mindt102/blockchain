import utils
from blockchain import Block, Blockchain, blockchain


class BlockMessage():
    command = b'block'
    __logger = utils.get_logger(__name__)

    def __init__(self, block: Block):
        self.__block = block

    def get_block(self) -> Block:
        return self.__block

    def serialize(self):
        return self.__block.serialize()

    @ classmethod
    def parse(cls, stream) -> tuple['BlockMessage', bytes]:
        block, stream = Block.parse(stream)
        return cls(block), stream

    def __repr__(self):
        return f'BlockMessage(block={self.__block})'

    @ classmethod
    def handler(cls, network, host, payload):
        peer = network.get_peer(host)
        if not (peer and peer.is_handshake_done()):
            cls.__logger.warning(
                f"Received block message from {host} before handshake")
            return
        blockmsg, _ = cls.parse(payload)
        block = blockmsg.get_block()
        blockchain.receive_new_block(block, sender=host)
        network.remove_requested(block.get_header().get_hash())
