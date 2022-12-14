import queue

from blockchain import Block, Transaction, TxIn, TxOut
from Role import Role
from utils import bits_to_target


class Blockchain(Role):
    '''Provide blockchain functionality'''

    def __init__(self, config: dict) -> None:
        self.config = config
        self.__reward = config["initial_reward"]
        self.__bits = config["initial_bits"]
        self.__genesis_block_path = config["genesis_block_path"]
        self.__genesis_block = self.__init_genesis_block()

        self.__blocks = dict()  # TODO: remove this
        self.__update_UTXO_set()
        super().__init__(blockchain=self)

    def run(self) -> None:
        while True:
            try:
                func, args, kwargs = self.q.get(timeout=self.q_timeout)
                func(*args, **kwargs)
            except queue.Empty:
                pass

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
        # TODO: IMPLEMENT @NHM
        return self.get_genesis_block()

    def get_block_by_hash(self, block_hash: bytes) -> Block:
        # TODO: IMPLEMENT @NHM
        if block_hash in self.__blocks:
            return self.__blocks[block_hash]
        else:
            return None

    def __init_genesis_block(self) -> Block:
        with open(self.__genesis_block_path, 'rb') as f:
            block = Block.parse(f.read())[0]
        return block

    # @Role._rpc
    def validate_block(self, block: Block) -> bool:
        return self.__validate_block(block)

    def __validate_block(self, block: Block) -> bool:
        # TODO: IMPLEMENT @Cong
        if not block.get_header().check_hash():
            return False

        txs = block.get_transactions()
        if not txs[0].is_coinbase():
            return False

        # block_merkle_root = compute_merkle_root(block)
        block_merkle_root = block.compute_merkle_root()
        if block_merkle_root != block.get_header().get_merkle_root():
            return False

        blockchain = self.get_blockchain()
        for i in range(1, len(txs)):
            tx = txs[i]
            if not blockchain.validate_transaction(tx) or tx.is_coinbase():
                return False

        return True

    def get_transaction_by_hash(self, tx_hash: bytes) -> Transaction:
        '''Query a transaction by its hash'''
        # TODO: IMPLEMENT @NHM

        # TODO: remove this
        return self.get_genesis_block().get_transactions()[0]

    def validate_transaction(self, tx: Transaction) -> bool:
        # TODO: IMPLEMENT @Hung + @Hien
        inputs = tx.get_inputs()

        # Evaluate the locking script of each input
        signing_data = tx.get_signing_data()
        for tx_in in inputs:
            if not self.__verify_txin(tx_in, signing_data):
                return False
        return True

    def __verify_txin(self, txin: TxIn, signing_data: str) -> bool:
        '''Verify a transaction input'''
        # If the input transaction is not in the UTXO set, return False
        prev_tx = txin.get_prev_tx()
        output_index = txin.get_output_index()
        if (prev_tx, output_index) not in self.__UTXO_set:
            return False

        # If the previous transaction does not exist, return False
        prev_tx = self.get_transaction_by_hash(prev_tx)
        if prev_tx is None:
            return False

        # If the output index is out of range, return False
        prev_outputs = prev_tx.get_outputs()
        if output_index >= len(prev_outputs):
            return False

        # If the signature is not valid, return False
        prev_output = prev_outputs[output_index]
        locking_script = prev_output.get_locking_script()
        unlocking_script = txin.get_unlocking_script()
        return (unlocking_script + locking_script).evaluate(signing_data)

    @Role._rpc
    def receive_new_block(self, block: Block, sender: str) -> None:
        existing_block = self.get_block_by_hash(block.get_header().get_hash())
        if existing_block:
            return
        if not self.__validate_block(block):
            return
        self.__add_block(block)
        self.get_miner().receive_new_block()
        self.get_network().broadcast_new_block(block, excludes=[sender])

    def __add_block(self, block: Block) -> None:
        # TODO: IMPLEMENT @NHM
        self.__blocks[block.get_header().get_hash()] = block
        pass

    def __update_UTXO_set(self) -> None:
        '''Query all unspent transaction outputs from the blockchain database'''
        # TODO: IMPLEMENT @Cong
        output_index = 0
        tx = self.get_genesis_block().get_transactions()[output_index]
        self.__UTXO_set: dict[tuple[bytes, int], TxOut] = {
            (tx.get_hash(), output_index): tx.get_output_by_index(output_index)
        }

    def get_UTXO_set(self, addr=[]) -> dict[tuple[bytes, int], TxOut]:
        '''Query unspent transaction outputs based on addresses'''
        if len(addr) == 0:
            return self.__UTXO_set
        else:
            # TODO: IMPLEMENT @NHM
            return self.__UTXO_set  # TODO: remove this
