import queue
from Role import Role
from blockchain import Script, Transaction, TxIn, TxOut
from utils import hash256
import utils


class Miner(Role):
    logger = utils.get_logger(__name__)

    def __init__(self) -> None:
        self.mempool = dict()
        self.mempool['test'] = self.__get_coinbase_tx()
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
        candidate_genesis = self.get_blockchain().genesis_block
        candidate_header = candidate_genesis.get_header()
        self.logger.info(f'nonce: {candidate_header.get_nonce()}')
        if candidate_header.check_hash():
            self.logger.info(
                f"Found genesis block")
            return True
        else:
            candidate_header.update_nonce()
            return False

    def __get_coinbase_tx(self) -> Transaction:
        wallet = self.get_wallet()
        addr = wallet.get_addr()
        priv_key = wallet.get_privkey().toDer()

        amount = self.get_blockchain().get_reward()

        txin = TxIn(b'\x00'*32, 0xffffffff,
                    unlocking_script=Script.get_unlock(priv_key))
        txout = TxOut(amount, Script.get_lock(addr))

        return Transaction([txin], [txout])

    def get_candidate_txs(self) -> list[Transaction]:
        return [self.__get_coinbase_tx()] + list(self.mempool.values())
