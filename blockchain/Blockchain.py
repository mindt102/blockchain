import queue

from blockchain import Block, Transaction, TxIn
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

        self.__blocks = list()  # TODO: remove this
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

    def get_block_by_hash(self, hash: bytes) -> Block:
        # TODO: IMPLEMENT @NHM
        return None

    def __init_genesis_block(self) -> Block:
        with open(self.__genesis_block_path, 'rb') as f:
            block = Block.parse(f.read())[0]
        return block

    @Role._rpc
    def validate_block(self, block: Block) -> bool:
        return self.__validate_block(block)

    def __validate_block(self, block: Block) -> bool:
        # TODO: IMPLEMENT @Cong
        return True

    def get_transaction_by_hash(self, hash: bytes) -> Transaction:
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
        prev_hash = txin.get_prev_hash()
        output_index = txin.get_output_index()
        if (prev_hash, output_index) not in self.__UTXO_set:
            return False

        # If the previous transaction does not exist, return False
        prev_tx = self.get_transaction_by_hash(prev_hash)
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
        block = self.get_block_by_hash(block.get_header().get_hash())
        if block:
            return
        if not self.__validate_block(block):
            return
        self.__add_block(block)
        self.get_miner().receive_new_block()
        self.get_network().broadcast_new_block(block, excludes=[sender])

    def __add_block(self, block: Block) -> None:
        # TODO: IMPLEMENT @NHM
        self.__blocks.append(block.get_header().get_hash())
        pass

    def __update_UTXO_set(self) -> None:
        '''Query all unspent transaction outputs from the blockchain database'''
        # TODO: IMPLEMENT @Cong
        output_index = 0
        tx = self.get_genesis_block().get_transactions()[output_index]
        self.__UTXO_set = {
            (tx.get_hash(), output_index): tx.get_outputs()[output_index]
        }

    def get_UTXO_set(self, addr=[]) -> dict:
        '''Query unspent transaction outputs based on addresses'''
        if len(addr) == 0:
            return self.__UTXO_set
        else:
            # TODO: IMPLEMENT @NHM
            return self.__UTXO_set  # TODO: remove this
