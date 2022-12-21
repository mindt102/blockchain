import queue

import database
from blockchain import Block, Transaction, TxIn, TxOut
from Role import Role
from utils import bits_to_target, get_logger


class Blockchain(Role):
    '''Provide blockchain functionality'''
    __logger = get_logger(__name__)

    def __init__(self, config: dict, db_config: dict, *args, **kwargs) -> None:
        self.__genesis_block_path = config["genesis_block_path"]
        self.__init_db(db_config)
        self.__reward = config["initial_reward"]
        self.__bits = config["initial_bits"]
        self.__genesis_block = self.__init_genesis_block()

        # self.__update_UTXO_set()
        super().__init__(blockchain=self, *args, **kwargs)

        self.__orphan_blocks: dict[bytes, Block] = dict()

        self.__is_ready = False

    def run(self) -> None:
        while self.active():
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

    def is_ready(self) -> bool:
        return self.__is_ready

    def set_ready(self) -> None:
        self.__is_ready = True
        self.__logger.info(
            f"Blockchain is ready. Current height: {self.get_height()}")

    def get_genesis_block(self) -> Block:
        return self.__genesis_block

    def get_genesis_block_path(self) -> str:
        return self.__genesis_block_path

    def get_top_hash(self) -> bytes:
        top_block, _ = database.get_top_block()
        return top_block.get_header().get_hash()

    def get_height(self) -> int:
        _, height = database.get_top_block()
        return height

    def get_block_locator_hashes(self) -> list[bytes]:
        _, height = database.get_top_block()
        step = 1
        hashes = []
        while height >= 0:
            header, _, _ = database.get_header_by_height(height)
            hashes.append(header.get_hash())
            if len(hashes) > 10:
                step *= 2
            height -= step
        return hashes

    def get_block_by_hash(self, block_hash: bytes) -> Block:
        return database.get_block_by_hash(block_hash)

    def get_header_by_hash(self, block_hash: bytes) -> Block:
        header, _, _ = database.get_header_by_hash(block_hash)
        return header

    def locate_common_block_hash(self, locator_hashes: list[bytes]) -> bytes:
        for block_hash in locator_hashes:
            if database.get_header_by_hash(block_hash):
                return block_hash
        return self.get_genesis_block().get_header().get_hash()

    def share_blocks_from_hash(self, common_block_hash: bytes) -> list[bytes]:
        _, _, common_height = database.get_header_by_hash(
            common_block_hash)
        max_height = database.get_max_height()

        block_hashes = []
        for height in range(common_height + 1, min(common_height + 500, max_height) + 1):
            header, _, _ = database.get_header_by_height(height)
            block_hashes.append(header.get_hash())
        return block_hashes

    def __init_genesis_block(self) -> Block:
        with open(self.__genesis_block_path, 'rb') as f:
            block = Block.parse(f.read())[0]
        return block

    def __init_db(self, config):
        try:
            database.create_db(config)
            genesis = self.__init_genesis_block()
            database.insert_block(genesis, height=0)
        except Exception:
            self.__logger.exception("Fail to initialize database.")

    def validate_block(self, block: Block) -> bool:
        # Check block header hash
        if not block.get_header().check_hash():
            self.__logger.debug("Invalid header hash")
            return False

        # Check first transaction is coinbase
        txs = block.get_transactions()
        if not txs[0].is_coinbase():
            self.__logger.debug("First tx is not coinbase")
            return False

        # Check merkle root received vs computed
        block_merkle_root = block.compute_merkle_root()
        if block_merkle_root != block.get_header().get_merkle_root():
            self.__logger.debug("Invalid merkel root")
            return False

        # Check validity of transactions
        for i in range(1, len(txs)):
            tx = txs[i]
            if tx.is_coinbase():
                self.__logger.debug(f"Transaction #{i} is coinbase")
                return False
            if not self.validate_transaction(tx):
                self.__logger.debug("Invalid transaction")
                return False

        return True

    def get_transaction_by_hash(self, tx_hash: bytes) -> Transaction:
        '''Query a transaction by its hash'''
        # TODO: IMPLEMENT @NHM
        return self.get_genesis_block().get_transactions()[0]

    def validate_transaction(self, tx: Transaction) -> bool:
        utxo_set = self.get_UTXO_set()
        inputs = tx.get_inputs()
        outputs = tx.get_outputs()
        signing_data = tx.get_signing_data()

        if len(inputs) == 0 or len(outputs) == 0:
            self.__logger.debug(
                f"Invalid input or output length: {len(inputs)} and {len(outputs)}")
            return False

        # Calculate total input amount
        input_sum = 0
        for txin in inputs:
            index = txin.get_output_index()
            prevtx = txin.get_prev_tx_hash()
            key = (prevtx, index)

            # Evaluate the locking script of each input
            if not self.__verify_txin(txin, signing_data):
                self.__logger.warning(
                    f"Invalid unlocking script. Txin: {txin}")
                return False

            # Not an unspent transaction outputs
            if key not in utxo_set:
                self.__logger.warning(f"Not an UTXO")
                return False
            input_sum += utxo_set[key].get_amount()

        # Calculate total output amount
        output_sum = 0
        for txout in outputs:
            output_sum += txout.get_amount()

        if input_sum < output_sum:
            self.__logger.debug(
                f"Input sum={input_sum} smaller than output sum={output_sum}")
            return False

        return True

    def __verify_txin(self, txin: TxIn, signing_data: str) -> bool:
        '''Verify a transaction input'''
        # If the input transaction is not in the UTXO set, return False
        prev_tx = txin.get_prev_tx_hash()
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
        block_hash = block.get_header().get_hash()

        db = database.DatabaseController()

        # Check if block already exists
        existing_header, _, _ = database.get_header_by_hash(block_hash, db=db)
        if existing_header:
            self.__logger.debug(
                f"Block {block_hash.hex()[-4:]} already exists")
            return

        # Check if block is valid
        if not self.validate_block(block):
            self.__logger.warning(f"Invalid block")
            return

        prev_block_hash = block.get_header().get_prev_block_hash()
        prev_header, _, prev_height = database.get_header_by_hash(
            prev_block_hash, db=db)

        # Check if block is orphan
        if prev_block_hash in self.__orphan_blocks:
            self.__logger.debug(
                f"Block {block_hash.hex()[-4:]} already in orphan blocks")
            return
        if prev_header is None:
            self.__logger.warning(
                f"==========> Orphan block: {prev_block_hash.hex()[-4:]} - {block_hash.hex()[-4:]}")
            self.__orphan_blocks[prev_block_hash] = block
            return

        # Check if block is forked
        if prev_block_hash != self.get_top_hash() and self.__is_ready:
            self.__logger.warning(f"Forked block")

        height = prev_height + 1
        database.insert_block(block, height, db=db)
        self.__logger.debug(
            f"==========> Block inserted: {block_hash.hex()[-4:]} at height {height}")

        parent_hash = block_hash
        while parent_hash in self.__orphan_blocks:
            orphan_block = self.__orphan_blocks[parent_hash]
            orphan_hash = orphan_block.get_header().get_hash()
            height += 1
            database.insert_block(orphan_block, height, db=db)
            self.__logger.debug(
                f"==========> Orphan block inserted: {database.get_block_by_hash(orphan_hash, db=db)}"
            )
            del self.__orphan_blocks[parent_hash]
            parent_hash = orphan_hash

        if self.get_top_hash() == block_hash and self.__is_ready:
            self.get_miner().receive_new_block()
            self.get_network().broadcast_new_block(block, excludes=[sender])
        db.close()

    # def __update_UTXO_set(self) -> None:
    #     '''Query all unspent transaction outputs from the blockchain database'''
    #     # TODO: IMPLEMENT @Cong

    def get_UTXO_set(self, addr=[]) -> dict[tuple[bytes, int], TxOut]:
        '''Query unspent transaction outputs based on addresses'''
        output_index = 0
        tx = self.get_genesis_block().get_transactions()[output_index]
        self.__UTXO_set: dict[tuple[bytes, int], TxOut] = {
            (tx.get_hash(), output_index): tx.get_output_by_index(output_index)
        }
        if len(addr) == 0:
            return self.__UTXO_set
        else:
            # TODO: IMPLEMENT @NHM
            return self.__UTXO_set
