from Role import Role
from blockchain import Block, Transaction
from utils import bits_to_target


class Blockchain(Role):
    '''Provide blockchain functionality'''

    def __init__(self, config: dict) -> None:
        self.config = config
        self.__reward = config["initial_reward"]
        self.__bits = config["initial_bits"]
        self.__genesis_block_path = config["genesis_block_path"]
        self.__genesis_block = self.__init_genesis_block()
        super().__init__(blockchain=self)

    def get_reward(self) -> int:
        return self.__reward

    def get_target(self) -> int:
        return bits_to_target(self.get_bits())

    def get_bits(self) -> bytes:
        return self.__bits

    def get_genesis_block(self) -> Block:
        return self.__genesis_block

    def get_genesis_block_path(self) -> str:
        return self.__genesis_block_path

    def get_latest_block(self) -> Block:
        #TODO: IMPLEMENT
        return self.get_genesis_block()

    def get_block_by_hash(self, hash: bytes) -> Block:
        #TODO: IMPLEMENT
        return None

    def __init_genesis_block(self) -> Block:
        with open(self.__genesis_block_path, 'rb') as f:
            block = Block.parse(f.read())[0]
        return block
