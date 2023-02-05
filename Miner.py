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
    def __init__(self, config) -> None:
        self.__config = config
        self.__candidate_block = None
        global _logger
        self.__logger = _logger

        self.__mempool: dict[bytes, Transaction] = dict()
        self.__mempool_lock = threading.Lock()

        self.__spent_txouts = set()
        super().__init__()

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
            self.__logger.info(f'Mining with nonce: {nonce}')
        if candidate_header.check_hash():
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

        prev_block_hash = prev_header.get_hash()
        height = prev_height + 1

        from blockchain import blockchain
        bits = blockchain.get_bits_by_height(height=height)

        # Reset candidate transactions
        with self.__mempool_lock:
            mempool_updated = False
            for tx in prev_txs:
                tx_hash = tx.get_hash()
                if tx_hash in self.__mempool:
                    del self.__mempool[tx_hash]
                    mempool_updated = True
                    # self.__logger.debug(
                    #     f"Removed tx from mempool: {tx_hash.hex()[-4:]}")
                for txin in tx.get_inputs():
                    prev_tx_hash = txin.get_prev_tx_hash()
                    output_index = txin.get_output_index()
                    if (prev_tx_hash, output_index) in self.__spent_txouts:
                        self.__spent_txouts.remove(
                            (prev_tx_hash, output_index))

            mempool_txs = list(self.__mempool.values())
            coinbase_tx = self.create_coinbase_tx(height=height)

            if mempool_updated:
                from api import emit_event
                emit_event('mempool', [tx.to_json()
                                       for tx in mempool_txs])

        candidate_txs = [coinbase_tx] + mempool_txs

        self.__candidate_block = Block(
            transactions=candidate_txs, prev_block_hash=prev_block_hash, bits=bits)

    @ Role._rpc  # type: ignore
    def receive_new_tx(self, tx: Transaction):
        with self.__mempool_lock:
            tx_hash = tx.get_hash()
            if tx_hash in self.__mempool:
                self.__logger.warning(
                    f"Tx already in mempool: {tx_hash.hex()[:4]}...{tx_hash.hex()[-4:]}")
                return
            self.__mempool[tx_hash] = tx
            self.__logger.info(
                f"New tx added to mempool: {tx_hash.hex()[:4]}...{tx_hash.hex()[-4:]}")
            for txin in tx.get_inputs():
                self.__spent_txouts.add(
                    (txin.get_prev_tx_hash(), txin.get_output_index()))
            mempool_txs = list(self.__mempool.values())

            from api import emit_event
            emit_event('mempool', [tx.to_json() for tx in mempool_txs])

    def create_coinbase_tx(self, height: int) -> Transaction:
        from wallet import address
        from blockchain import REWARD

        amount = REWARD

        txin = TxIn(prev_tx=32*b'\x00', output_index=0xffffffff,
                    unlocking_script=Script(cmds=[height.to_bytes(4, 'little')]))
        txout = TxOut(amount, addr=address)

        tx = Transaction([txin], [txout])
        return tx

    def get_mempooltx_by_hash(self, tx_hash: bytes) -> Transaction:
        '''Get transaction by hash from mempool'''
        result = None
        with self.__mempool_lock:
            if tx_hash in self.__mempool:
                result = self.__mempool[tx_hash]
        return result

    def get_spent_txouts(self) -> set[tuple[bytes, int]]:
        return self.__spent_txouts

    def get_candidate_block(self) -> Block:
        return self.__candidate_block

    def get_mempool(self) -> list[Transaction]:
        return list(self.__mempool.values())


miner = Miner(config=utils.config['miner'])
_logger.info('Miner initialized.')
