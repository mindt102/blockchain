import queue
import threading
# from RoleContainer import RoleContainer

import utils


class Role(threading.Thread):
    __logger = utils.get_logger(__name__)
    # __roles = RoleContainer()
    __run_event = threading.Event()

    def __init__(self, wallet=None, miner=None, blockchain=None, network=None):  # type: ignore
        self.q = queue.Queue()
        self.q_timeout = 1.0/60
        # if wallet:
        #     self.__roles.set_wallet(wallet)
        # if miner:
        #     self.__roles.set_miner(miner)
        # if blockchain:
        #     self.__roles.set_blockchain(blockchain)
        # if network:
        #     self.__roles.set_network(network)

        if not self.active():
            self.__run_event.set()
        super().__init__()

    def _rpc(func):  # type: ignore
        def wrapper(self, *args, **kwargs):
            self.q.put((func, (self, *args), kwargs))
        return wrapper

    # @_rpc  # type: ignore
    # def test(self, message: str = "test"):
    #     self.__logger.debug(message)

    # @classmethod
    # def get_wallet(cls):
    #     return cls.__roles.get_wallet()

    # @classmethod
    # def get_miner(cls):
    #     return cls.__roles.get_miner()

    # @classmethod
    # def get_blockchain(cls):
    #     return cls.__roles.get_blockchain()

    # @classmethod
    # def get_network(cls):
    #     return cls.__roles.get_network()

    def active(self):
        return self.__run_event.is_set()

    @classmethod
    def deactivate(cls):
        cls.__run_event.clear()
