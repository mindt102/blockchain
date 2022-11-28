

class RoleContainer:
    def __init__(self):
        self.__wallet = None  # type: ignore
        self.__miner = None  # type: ignore
        self.__blockchain = None  # type: ignore
        self.__network = None  # type: ignore

    def set_wallet(self, wallet):
        self.__wallet = wallet

    def set_miner(self, miner):
        self.__miner = miner

    def set_blockchain(self, blockchain):
        self.__blockchain = blockchain

    def set_network(self, network):
        self.__network = network

    def get_wallet(self):
        return self.__wallet

    def get_miner(self):
        return self.__miner

    def get_blockchain(self):
        return self.__blockchain

    def get_network(self):
        return self.__network
