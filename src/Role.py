import queue
import threading
from RoleContainer import RoleContainer

import utils


class Role(threading.Thread):
    logger = utils.get_logger(__name__)
    __roles = RoleContainer()

    def __init__(self, wallet=None, miner=None, blockchain=None):  # type: ignore
        self.q = queue.Queue()
        self.q_timeout = 1.0/60
        if wallet:
            self.__roles.set_wallet(wallet)
        if miner:
            self.__roles.set_miner(miner)
        if blockchain:
            self.__roles.set_blockchain(blockchain)
        super().__init__()

    def _rpc(func):  # type: ignore
        def wrapper(self, *args, **kwargs):
            self.q.put((func, (self, *args), kwargs))
        return wrapper

    @_rpc  # type: ignore
    def test(self):
        self.logger.debug('test')

    def get_wallet(self):
        return self.__roles.get_wallet()

    def get_miner(self):
        return self.__roles.get_miner()

    def get_blockchain(self):
        return self.__roles.get_blockchain()
