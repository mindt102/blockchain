from blockchain.BlockHeader import BlockHeader
from blockchain.Transaction import Transaction
from utils import hash256


class Block:
    def __init__(self, transactions: list[Transaction], prev_block_hash: bytes = None, bits: int = None, header: BlockHeader = None) -> None:
        self.__transactions = transactions
        if header:
            self.__header = header
        elif prev_block_hash and bits:
            self.__header = BlockHeader(
                prev_block_hash, self.compute_merkle_root(), bits)
        else:
            raise ValueError(
                'Either header or prev_block_hash and bits must be provided')

    def get_header(self) -> BlockHeader:
        return self.__header

    def compute_merkle_root(self) -> bytes:
        # TODO: implement
        return hash256(self.__transactions[0].serialize())

    def get_transactions(self) -> list[Transaction]:
        return self.__transactions

    # def set_header(self, header: BlockHeader) -> None:
    #     self.__header = header
    def to_json(self) -> dict:
        return {
            'header': self.__header.to_json(),
            'transactions': [tx.to_json() for tx in self.__transactions]
        }

    def __repr__(self) -> str:
        return f'''Block({self.to_json()})'''

    def serialize(self) -> bytes:
        return self.__header.serialize() + b''.join([tx.serialize() for tx in self.__transactions])

    @classmethod
    def parse(cls, stream: bytes) -> tuple['Block', bytes]:
        header, stream = BlockHeader.parse(stream)
        txs = []
        while stream:
            tx, stream = Transaction.parse(stream)
            txs.append(tx)
        block = cls(transactions=txs, header=header)
        # block.set_header(header)
        return block, stream

    # def insert(self):
    #     # blockHeaderId = self.get_header().insert()
    #     header_id = database.insert_header(self.get_header())
    #     print(header_id)
    #     for tx in self.get_transactions():
    #         # tx.insert(header_id)
    #         database.insert_tx(tx=tx, header_id=header_id)
