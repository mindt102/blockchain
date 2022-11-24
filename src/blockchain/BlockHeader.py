import random
import time
from typing import Self

from utils import hash256, bits_to_target


class BlockHeader:
    def __init__(self, prev_block_hash: bytes, merkle_root: bytes, bits: int, nonce: int = 0, timestamp: int = None) -> None:
        self.__prev_block_hash = prev_block_hash
        self.__merkle_root = merkle_root
        if not timestamp:
            timestamp = int(time.time())
        self.__timestamp = timestamp
        self.__bits = bits
        self.__nonce = 10000 * random.randint(10, 100)

    def check_hash(self) -> bool:
        hash_result = hash256(self.serialize())
        return int.from_bytes(hash_result) < bits_to_target(self.get_bits())

    def update_nonce(self) -> None:
        self.__nonce += 1

    def get_nonce(self) -> int:
        return self.__nonce

    def get_bits(self) -> int:
        return self.__bits

    def serialize(self) -> bytes:
        return self.__prev_block_hash + self.__merkle_root + self.__timestamp.to_bytes(4, 'little') + self.get_bits().to_bytes(4, 'little') + self.__nonce.to_bytes(4, 'little')

    @classmethod
    def parse(cls, stream: bytes) -> tuple[Self, bytes]:
        prev_block_hash = stream[:32]
        stream = stream[32:]
        merkle_root = stream[:32]
        stream = stream[32:]
        timestamp = int.from_bytes(stream[:4], 'little')
        stream = stream[4:]
        bits = int.from_bytes(stream[:4], 'little')
        stream = stream[4:]
        nonce = int.from_bytes(stream[:4], 'little')
        stream = stream[4:]
        return cls(prev_block_hash, merkle_root, bits, nonce, timestamp), stream
