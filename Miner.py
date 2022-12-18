import queue

import utils
from blockchain import Block, Blockchain, Transaction, TxIn, TxOut
from Role import Role


class Miner(Role):
    logger = utils.get_logger(__name__)

    def __init__(self, config) -> None:
        self.__mempool = dict()
        # self.__mempool['test'] = self.create_coinbase_tx()
        self.__config = config
        self.__new_block_found = True
        self.__new_block_received = False
        self.__candidate_block = None

        self.__is_network_ready = False
        super().__init__(miner=self)

    def run(self):
        while True:
            try:
                func, args, kwargs = self.q.get(timeout=self.q_timeout)
                func(*args, **kwargs)
            except queue.Empty:
                if self.__is_network_ready:
                    if self.__idle():
                        break

    def __idle(self):
        if self.__new_block_found:
            self.logger.info("Restart mining")
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
                self.get_network().broadcast_new_block(self.__candidate_block)
                # return True
            else:
                candidate_header.update_nonce()
        # if self.__new_block_received:
        #     return True

    # @Role._rpc  # type: ignore
    def receive_new_block(self):
        # TODO: IMPLEMENT
        self.__new_block_received = True
        self.logger.debug('New block received')
        self.__new_block_found = True

    def reset_candidate_block(self):
        candidate_txs = self.__get_candidate_txs()
        blockchain: Blockchain = self.get_blockchain()
        prev_block = blockchain.get_top_block()
        prev_hash = prev_block.get_header().get_hash()
        bits = blockchain.get_bits()
        self.__candidate_block = Block(candidate_txs, prev_hash, bits)

    def create_coinbase_tx(self) -> Transaction:
        wallet = self.get_wallet()
        addr = wallet.get_addr()

        amount = self.get_blockchain().get_reward()

        txin = TxIn(prev_tx=32*b'\x00', output_index=0xffffffff)
        txout = TxOut(amount, addr=addr)

        tx = Transaction([txin], [txout])
        return tx

    def __get_candidate_txs(self) -> list[Transaction]:
        mempool_txs = list(self.__mempool.values())
        coinbase_tx = self.create_coinbase_tx()
        self.__mempool.clear()
        return [coinbase_tx] + mempool_txs

    @ Role._rpc  # type: ignore
    def get_mempooltx_by_hash(self, tx_hash: bytes) -> Transaction:
        '''Get transaction by hash from mempool'''
        # TODO: TEST
        if tx_hash in self.__mempool:
            return self.__mempool[tx_hash]

    def set_network_status(self, status: bool = True):
        self.__is_network_ready = status

    def get_network_status(self) -> bool:
        return self.__is_network_ready
