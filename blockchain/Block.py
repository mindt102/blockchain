from blockchain.BlockHeader import BlockHeader
from blockchain.Transaction import Transaction
from utils import hash256


class Block:
    def __init__(self, transactions: list[Transaction], prev_block_hash: bytes = None, bits: int = None) -> None:
        self.__transactions = transactions
        if prev_block_hash and bits:
            self.__header = BlockHeader(
                prev_block_hash, self.get_merkle_root(), bits)

    def get_header(self) -> BlockHeader:
        return self.__header

    def get_merkle_root(self) -> bytes:
        # TODO: implement
        return hash256(self.__transactions[0].serialize())

    def get_transactions(self) -> list[Transaction]:
        return self.__transactions

    def __set_header(self, header: BlockHeader) -> None:
        self.__header = header

    def __repr__(self) -> str:
        return f'''Block(
    header = {self.__header},
    transactions = {self.__transactions}
)'''

    def serialize(self) -> bytes:
        return self.__header.serialize() + b''.join([tx.serialize() for tx in self.__transactions])

    @classmethod
    def parse(cls, stream: bytes) -> tuple['Block', bytes]:
        header, stream = BlockHeader.parse(stream)
        txs = []
        while stream:
            tx, stream = Transaction.parse(stream)
            txs.append(tx)
        block = cls(txs, header.get_prev_block_hash(), header.get_bits())
        block.__set_header(header)
        return block, stream
