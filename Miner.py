import queue
import threading

import utils
from blockchain.Script import Script
from blockchain.Transaction import Transaction
from blockchain.TxIn import TxIn
from blockchain.TxOut import TxOut
from blockchain.Block import Block
from Role import Role
import database

_logger = utils.get_logger(__name__)


class Miner(Role):
    def __init__(self, config, *args, **kwargs) -> None:
        # self.__mempool['test'] = self.create_coinbase_tx()
        self.__config = config
        self.__new_block_found = True
        self.__candidate_block = None
        global _logger
        self.__logger = _logger
        super().__init__(miner=self, *args, **kwargs)

        self.__mempool: dict[bytes, Transaction] = dict()
        self.__mempool_lock = threading.Lock()

        self.__spent_txouts = set()

    def run(self):
        self.__logger.info('Start mining')
        self.__reset_candidate_block()
        from blockchain import blockchain
        from network import network
        while self.active():
            try:
                func, args, kwargs = self.q.get(timeout=self.q_timeout)
                func(*args, **kwargs)
            except queue.Empty:
                if network.is_ready() and blockchain.is_ready():
                    if self.__idle():
                        break

    def __idle(self):
        candidate_header = self.__candidate_block.get_header()
        nonce = candidate_header.get_nonce()
        if self.__config['logging_rate'] and nonce % self.__config['logging_rate'] == 0:
            self.__logger.info(f'nonce: {nonce}')
        if candidate_header.check_hash():
            # self.__new_block_found = True
            self.__logger.info(
                f'New block found: {candidate_header.get_hash().hex()[-4:]}')
            from blockchain import blockchain
            blockchain.receive_new_block(self.__candidate_block)
            self.__reset_candidate_block()
        else:
            candidate_header.update_nonce()

    @Role._rpc  # type: ignore
    def receive_new_block(self):
        self.__reset_candidate_block()

    def __reset_candidate_block(self):
        top_block, prev_height = database.get_top_block()
        prev_header = top_block.get_header()
        prev_txs = top_block.get_transactions()
        self.__logger.debug(
            f"Txs added to the chain: {' '.join([tx.get_hash().hex()[-4:] for tx in prev_txs])}")
        # self.__logger.debug(
        #     f"Txs added to the chain: {prev_txs}")

        prev_block_hash = prev_header.get_hash()
        height = prev_height + 1

        from blockchain import blockchain
        bits = blockchain.get_bits_by_height(height=height)

        # Reset candidate transactions
        with self.__mempool_lock:
            for tx in prev_txs:
                tx_hash = tx.get_hash()
                if tx_hash in self.__mempool:
                    del self.__mempool[tx_hash]
                    self.__logger.debug(
                        f"Removed tx from mempool: {tx_hash.hex()[-4:]}")
                for txin in tx.get_inputs():
                    prev_tx_hash = txin.get_prev_tx_hash()
                    output_index = txin.get_output_index()
                    if (prev_tx_hash, output_index) in self.__spent_txouts:
                        self.__spent_txouts.remove(
                            (prev_tx_hash, output_index))

            mempool_txs = list(self.__mempool.values())
            self.__logger.debug(
                f"Mempool txs: {' '.join([tx.get_hash().hex()[-4:] for tx in mempool_txs])}")
            # self.__logger.debug(
            #     f"Mempool txs: {mempool_txs}")
            coinbase_tx = self.create_coinbase_tx(height=height)
        candidate_txs = [coinbase_tx] + mempool_txs

        self.__candidate_block = Block(
            transactions=candidate_txs, prev_block_hash=prev_block_hash, bits=bits)
        self.__logger.debug(
            f"Candidate transactions: {' '.join([tx.get_hash().hex()[-4:] for tx in candidate_txs])}")
        self.__logger.debug(
            f"Candidate bits: {hex(bits)}")

    @ Role._rpc  # type: ignore
    def receive_new_tx(self, tx: Transaction):
        with self.__mempool_lock:
            if tx.get_hash() in self.__mempool:
                self.__logger.warning(
                    f"Tx already in mempool: {tx.get_hash()}")
                return
            self.__mempool[tx.get_hash()] = tx
            for txin in tx.get_inputs():
                self.__spent_txouts.add(
                    (txin.get_prev_tx_hash(), txin.get_output_index()))
            self.__logger.debug(
                f"Added new tx to mempool: {tx.get_hash().hex()[-4:]}")

    def create_coinbase_tx(self, height: int) -> Transaction:
        from wallet import address
        from blockchain import blockchain

        amount = blockchain.get_reward()

        txin = TxIn(prev_tx=32*b'\x00', output_index=0xffffffff,
                    unlocking_script=Script(cmds=[height.to_bytes(4, 'little')]))
        txout = TxOut(amount, addr=address)

        tx = Transaction([txin], [txout])
        return tx

    # @ Role._rpc  # type: ignore
    def get_mempooltx_by_hash(self, tx_hash: bytes) -> Transaction:
        '''Get transaction by hash from mempool'''
        result = None
        with self.__mempool_lock:
            if tx_hash in self.__mempool:
                result = self.__mempool[tx_hash]
        return result

    def get_spent_txouts(self) -> set[tuple[bytes, int]]:
        return self.__spent_txouts


miner = Miner(config=utils.config['miner'])
_logger.info('Miner initialized.')
