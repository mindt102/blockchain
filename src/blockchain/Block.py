from blockchain.BlockHeader import BlockHeader
from blockchain.Transaction import Transaction
from utils import hash256


class Block:
    def __init__(self, candidate_txs: list[Transaction], prev_block_hash: bytes, target: int) -> None:
        self.__transactions = candidate_txs
        self.__header = BlockHeader(
            prev_block_hash, self.get_merkle_root(), target
        )

    def get_header(self) -> BlockHeader:
        return self.__header

    def get_merkle_root(self) -> bytes:
        # TODO: implement
        return hash256(self.__transactions[0].serialize())
