import queue
from Role import Role
from blockchain import Block, Script, Transaction, TxIn, TxOut
from utils import hash256
import utils


class Miner(Role):
    logger = utils.get_logger(__name__)

    def __init__(self, config) -> None:
        self.__mempool = dict()
        self.__mempool['test'] = self.create_coinbase_tx()
        self.__config = config
        self.__new_block_found = True
        self.__new_block_received = False
        self.__candidate_block = None
        super().__init__(miner=self)

    def run(self):
        while True:
            try:
                func, args, kwargs = self.q.get(timeout=self.q_timeout)
                func(*args, **kwargs)
            except queue.Empty:
                if self.__idle():
                    break

    def __idle(self):
        if self.__new_block_found:
            self.reset_candidate_block()
            self.__new_block_found = False
        else:
            candidate_header = self.__candidate_block.get_header()
            nonce = candidate_header.get_nonce()
            if nonce % self.__config['logging_rate'] == 0:
                self.logger.info(f'nonce: {nonce}')
            if candidate_header.check_hash():
                self.__new_block_found = True
                self.logger.info('New block found')
                # print(self.__candidate_block)
                self.get_network().broadcast_new_block(candidate_header.get_hash())
                return True
            else:
                candidate_header.update_nonce()
        if self.__new_block_received:
            return True

    @Role._rpc  # type: ignore
    def receive_new_block(self):
        # TODO: IMPLEMENT
        self.__new_block_received = True

    def reset_candidate_block(self):
        candidate_txs = self.__get_candidate_txs()
        prev_block = self.get_blockchain().get_latest_block()
        prev_hash = prev_block.get_header().get_hash()
        bits = self.get_blockchain().get_bits()
        self.__candidate_block = Block(candidate_txs, prev_hash, bits)

    def create_coinbase_tx(self) -> Transaction:
        wallet = self.get_wallet()
        addr = wallet.get_addr()
        priv_key = wallet.get_privkey().toDer()

        amount = self.get_blockchain().get_reward()

        txin = TxIn(b'\x00'*32, 0xffffffff,
                    unlocking_script=Script.get_unlock(priv_key))
        txout = TxOut(amount, Script.get_lock(addr))

        return Transaction([txin], [txout])

    def __get_candidate_txs(self) -> list[Transaction]:
        mempool_txs = list(self.__mempool.values())
        coinbase_tx = self.create_coinbase_tx()
        self.__mempool.clear()
        return [coinbase_tx] + mempool_txs

    @Role._rpc  # type: ignore
    def get_tx_by_hash(self, tx_hash: bytes) -> Transaction:
        # TODO: IMPLEMENT
        return None
