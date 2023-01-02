import random
import time
# from database.DatabaseController import DatabaseController


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
        self.__height = None

    def get_hash(self) -> bytes:
        return hash256(self.serialize())

    def check_hash(self) -> bool:
        return int.from_bytes(self.get_hash(), byteorder='big') < bits_to_target(self.get_bits())

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

    def get_merkle_root(self) -> bytes:
        return self.__merkle_root

    def set_height(self, height: int) -> None:
        self.__height = height

    def get_height(self) -> int:
        return self.__height

    def to_json(self) -> dict:
        return {
            'height': self.get_height(),
            'prev_block_hash': self.__prev_block_hash.hex(),
            'merkle_root': self.__merkle_root.hex(),
            'timestamp': self.__timestamp,
            'bits': hex(self.get_bits()),
            'nonce': self.__nonce,
            'hash': self.get_hash().hex()
        }

    def __repr__(self) -> str:
        return f'''BlockHeader({self.to_json()})'''

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

    # __tableName = "block_headers"
    # __tableCol = ["prev_hash", "hash", "merkel_root",
    #               "timestamp", "nonce", "bits", "height"]

    # @classmethod
    # def getMaxHeight(cls):
    #     __db = DatabaseController()
    #     res = __db.fetchOne(
    #         "SELECT MAX(height) FROM {}".format(cls.__tableName))
    #     if res[0]:
    #         return res[0]
    #     return 0

    # def insert(self):
    #     values = (self.__prev_block_hash, self.get_hash(),
    #               self.__merkle_root, self.__timestamp, self.__nonce, self.__bits, self.getMaxHeight()+1)
    #     __db = DatabaseController()
    #     return __db.insert(self.__tableName, self.__tableCol, values)
