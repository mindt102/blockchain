

class RoleContainer:
    def __init__(self):
        self.__wallet = None  # type: ignore
        self.__miner = None  # type: ignore
        self.__blockchain = None  # type: ignore

    def set_wallet(self, wallet):
        self.__wallet = wallet

    def set_miner(self, miner):
        self.__miner = miner

    def set_blockchain(self, blockchain):
        self.__blockchain = blockchain

    def get_wallet(self):
        return self.__wallet

    def get_miner(self):
        return self.__miner

    def get_blockchain(self):
        return self.__blockchain
