import random
import time


from utils import hash256, bits_to_target


class BlockHeader:
    def __init__(self, prev_block_hash: bytes, merkle_root: bytes, bits: int, nonce: int = 0, timestamp: int = None) -> None:
        self.__prev_block_hash = prev_block_hash
        self.__merkle_root = merkle_root
        if not timestamp:
            timestamp = int(time.time())
        self.__timestamp = timestamp
        self.__bits = bits
        if not nonce:
            nonce = 10000 * random.randint(10, 100)
        self.__nonce = nonce

    def get_hash(self) -> bytes:
        return hash256(self.serialize())

    def check_hash(self) -> bool:
        return int.from_bytes(self.get_hash()) < bits_to_target(self.get_bits())

    def update_nonce(self) -> None:
        self.__nonce += 1

    def get_nonce(self) -> int:
        return self.__nonce

    def get_bits(self) -> int:
        return self.__bits

    def get_timestamp(self) -> int:
        return self.__timestamp

    def get_prev_block_hash(self) -> bytes:
        return self.__prev_block_hash

    def __repr__(self) -> str:
        return f'''BlockHeader(
    prev_block_hash={self.__prev_block_hash.hex()}, 
    merkle_root={self.__merkle_root.hex()}, 
    timestamp={self.__timestamp}, 
    bits={self.__bits}, 
    nonce={self.__nonce}
)'''

    def serialize(self) -> bytes:
        return self.__prev_block_hash + self.__merkle_root + self.__timestamp.to_bytes(4, 'little') + self.get_bits().to_bytes(4, 'little') + self.__nonce.to_bytes(4, 'little')

    @classmethod
    def parse(cls, stream: bytes) -> tuple['BlockHeader', bytes]:
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
