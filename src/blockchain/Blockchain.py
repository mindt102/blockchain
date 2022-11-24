from Role import Role
from blockchain import Block, Transaction
from utils import bits_to_target


class Blockchain(Role):
    def __init__(self, config: dict) -> None:
        self.config = config
        self.__reward = config["initial_reward"]
        self.__bits = config["initial_bits"]
        self.genesis_block = self.init_genesis_block()
        super().__init__(blockchain=self)

    def get_reward(self) -> int:
        return self.__reward

    def get_target(self) -> int:
        return bits_to_target(self.get_bits())

    def get_bits(self) -> bytes:
        return self.__bits

    def init_genesis_block(self) -> Block:
        coinbase_tx = Transaction.parse(
            b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x01Lv0t\x02\x01\x01\x04 \xcf8\x0c\xf1\xfc\xf4> <{\xbc|\xc7\x03\x81h\xb3\x17\xe5\x02ZXs.$\x90\x8e\xfc\x069\x9f9\xa0\x07\x06\x05+\x81\x04\x00\n\xa1D\x03B\x00\x04\xf7\x99\x83\xf8\x01\x85\x0e,PM\xddpa\xe3\xcb\xec\xa3\xd6\xef?%\xd3\xae?\x946\x9c\x10.\x93\t\xbeI\x03\x1f\xa9\xca\xf0 \x94{\x12s\xf6\xc3\xa7\t\x1a\xd6G\x83*\x84\xe8\xcb\xc6\xd5\xae\x01\x94\xc5;\xd5\xa9\x01\x00\x00\x002\x00\x00\x00\x00\x00\x00\x00\x05\x01v\x01\xa9"17GGQa3xa8jDwzm2qAwCapocYQZHWGQth7\x01\x88\x01\xac')
        return Block([coinbase_tx], b'\x00'*32, self.get_bits())
