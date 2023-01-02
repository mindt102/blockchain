import queue

import database
from blockchain import Block, Transaction, TxIn, TxOut
from Role import Role
from utils import bits_to_target, get_logger, target_to_bits
from Miner import miner


class Blockchain(Role):
    '''Provide blockchain functionality'''
    __logger = get_logger(__name__)

    def __init__(self, config: dict, db_config: dict, *args, **kwargs) -> None:
        self.__genesis_block_path = config["genesis_block_path"]
        # self.__init_db(db_config)
        self.__reward = config["initial_reward"]
        self.__initial_bits = config["initial_bits"]
        self.__difficulty_adjustment_interval = config["difficulty_adjustment_interval"]
        self.__expected_mine_time = config["expected_mine_time"]
        # self.__genesis_block = self.__init_genesis_block()

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

    # def get_target(self) -> int:
    #     return bits_to_target(self.get_bits_by_height())

    def get_bits_by_height(self, height: int) -> bytes:
        if not self.__difficulty_adjustment_interval:
            return self.__initial_bits
        if height < self.__difficulty_adjustment_interval:
            return self.__initial_bits
        if (height % self.__difficulty_adjustment_interval) != 0:
            bits = database.get_bits_by_height(height - 1)
            if not bits:
                self.__logger.error(f"Can't get bits at height {height - 1}")
            return bits

        prev_interval_start_block = database.get_block_by_height(
            height - self.__difficulty_adjustment_interval)
        prev_interval_end_block = database.get_block_by_height(height - 1)

        dtime = (prev_interval_end_block.get_header().get_timestamp(
        ) - prev_interval_start_block.get_header().get_timestamp()) // 60
        self.__logger.debug(
            f"Difficulty adjustment interval: {dtime:.2f} minutes")

        prev_interval_bits = prev_interval_end_block.get_header().get_bits()
        prev_interval_target = bits_to_target(prev_interval_bits)
        self.__logger.debug(
            f"Previous interval target: {prev_interval_target:064x} - {prev_interval_target}")

        new_target = (prev_interval_target * dtime) // (
            self.__expected_mine_time * self.__difficulty_adjustment_interval)

        self.__logger.debug(f"New target: {new_target:064x} - {new_target}")
        self.__logger.debug(
            f"Adjustment factor: {new_target / prev_interval_target:.4f}")

        initial_target = bits_to_target(self.__initial_bits)
        if new_target > initial_target:
            new_target = initial_target

        self.__logger.debug(f"New target: {new_target:064x} - {new_target}")

        new_bits = target_to_bits(new_target)
        self.__logger.debug(f"New bits: {new_bits:08x} - {new_bits}")
        return new_bits

    def is_ready(self) -> bool:
        return self.__is_ready

    def set_ready(self) -> None:
        self.__is_ready = True
        self.__logger.info(
            # f"Blockchain is ready. Current height: {self.get_height()}")
            f"Blockchain is ready. Current height: {database.get_max_height()}")

    def get_genesis_block(self) -> Block:
        return self.__genesis_block

    def get_genesis_block_path(self) -> str:
        return self.__genesis_block_path

    def get_top_hash(self) -> bytes:
        top_block, _ = database.get_top_block()
        return top_block.get_header().get_hash()

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

    def get_utxo(self, addrs: list[str] = []) -> dict[tuple[bytes, int], TxOut]:
        '''
        Filter out spent outputs in mempool from the UTXO set of the database
        Returns:
            dict[tuple[bytes, int], TxOut]: UTXO set
        '''
        utxo_set = database.get_utxo(addrs)
        self.__logger.debug(f"UTXO set: {len(utxo_set)}")
        spent_set = miner.get_spent_txouts()
        self.__logger.debug(f"Spend set: {len(spent_set)}")
        for key in spent_set:
            utxo_set.pop(key, None)
        return utxo_set

    def validate_block(self, block: Block) -> bool:
        header = block.get_header()
        # # Check block bits
        # if header.get_bits() != self.get_bits_by_height(height=height):
        #     self.__logger.debug("Invalid bits")
        #     return False

        # Check block header hash
        if not header.check_hash():
            self.__logger.debug("Invalid header hash")
            return False

        txs = block.get_transactions()
        # Check first transaction is coinbase
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

    def validate_block_bits(self, bits: int, height: int) -> bool:
        return bits == self.get_bits_by_height(height=height)

    def validate_transaction(self, tx: Transaction) -> bool:
        utxo_set = database.get_utxo()
        inputs = tx.get_inputs()
        outputs = tx.get_outputs()
        signing_data = tx.get_signing_data()

        # Check if there are any inputs or outputs
        if len(inputs) == 0 or len(outputs) == 0:
            self.__logger.debug(
                f"Invalid input or output length: {len(inputs)} and {len(outputs)}")
            return False

        # Calculate total input amount
        input_sum = 0
        spent_txouts = set()
        for txin in inputs:
            index = txin.get_output_index()
            prevtx = txin.get_prev_tx_hash()
            key = (prevtx, index)

            # Evaluate the locking script of each input
            if not self.__verify_txin(txin, signing_data, utxo_set, spent_txouts):
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
            self.__logger.info(
                f"Input sum={input_sum} smaller than output sum={output_sum}")
            return False

        return True

    def __verify_txin(self, txin: TxIn, signing_data: str, utxo_set: dict, spent_txouts: set) -> bool:
        '''Verify a transaction input'''
        # If the input transaction is not in the UTXO set, return False
        prev_tx = txin.get_prev_tx_hash()
        output_index = txin.get_output_index()
        if (prev_tx, output_index) not in utxo_set and (prev_tx, output_index) not in spent_txouts:
            self.__logger.warning("Input transaction not in UTXO set")
            return False

        # If the previous transaction does not exist, return False
        prev_tx, _ = database.get_tx_by_hash(prev_tx)
        if prev_tx is None:
            self.__logger.warning("Previous transaction does not exist")
            return False

        # If the output index is out of range, return False
        prev_outputs = prev_tx.get_outputs()
        if output_index >= len(prev_outputs):
            self.__logger.warning("Output index out of range")
            return False

        # If the signature is not valid, return False
        prev_output = prev_outputs[output_index]
        locking_script = prev_output.get_locking_script()
        unlocking_script = txin.get_unlocking_script()
        if not (unlocking_script + locking_script).evaluate(signing_data):
            self.__logger.warning("Signature is not valid")
            return False

        spent_txouts.add((prev_tx, output_index))
        return True

    @ Role._rpc
    def receive_new_block(self, block: Block, sender: str = None) -> None:
        db = database.DatabaseController()
        header = block.get_header()
        block_hash = header.get_hash()

        # Check if block already exists
        existing_header, _, _ = database.get_header_by_hash(
            block_hash, db=db)
        if existing_header:
            # self.__logger.debug(
            #     f"Block {block_hash.hex()[-4:]} already exists")
            return

        # Check if block is valid
        if not self.validate_block(block):
            self.__logger.warning(f"Invalid block")
            return

        prev_block_hash = header.get_prev_block_hash()
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
        if prev_block_hash != self.get_top_hash() and self.is_ready():
            self.__logger.warning(f"Forked block")

        # Check if block's bits are valid
        height = prev_height + 1
        if not self.validate_block_bits(header.get_bits(), height):
            self.__logger.warning(f"Invalid bits")
            return

        database.insert_block(block, height, db=db)
        self.__logger.debug(
            f"==========> Block inserted: {block_hash.hex()[-4:]} at height {height}")

        parent_hash = block_hash
        valid_orphans = True
        while parent_hash in self.__orphan_blocks:
            orphan_block = self.__orphan_blocks[parent_hash]
            orphan_hash = orphan_block.get_header().get_hash()
            height += 1
            if valid_orphans and self.validate_block_bits(orphan_block.get_header().get_bits(), height):
                database.insert_block(orphan_block, height, db=db)
                self.__logger.debug(
                    f"==========> Orphan block inserted: {database.get_block_by_hash(orphan_hash, db=db)}")
            else:
                valid_orphans = False
            # database.insert_block(orphan_block, height, db=db)
            # self.__logger.debug(
            #     f"==========> Orphan block inserted: {database.get_block_by_hash(orphan_hash, db=db)}"
            # )
            del self.__orphan_blocks[parent_hash]
            parent_hash = orphan_hash

        if self.get_top_hash() == block_hash and self.__is_ready:
            miner.receive_new_block()
            from network import network
            network.broadcast_new_block(block, excludes=[sender])
        db.close()

    @ Role._rpc
    def receive_new_tx(self, tx: Transaction, sender: str = None) -> None:
        db = database.DatabaseController()
        tx_hash = tx.get_hash()
        if sender:  # If sender is not None, it means the transaction is received from other peers, else it is received from the api
            if tx.is_coinbase():
                self.__logger.warning(f"Received coinbase transaction")
                return

            # Check if transaction already exists in the mempool or database
            existing_tx = miner.get_mempooltx_by_hash(tx_hash) or database.get_tx_by_hash(
                tx_hash)[0]
            if existing_tx:
                self.__logger.debug(
                    f"Transaction {tx_hash.hex()[-4:]} already exists")
                return

        # Check if transaction is valid
        if not self.validate_transaction(tx):
            self.__logger.warning(f"Invalid transaction")
            return

        # if self.is_ready():
        # self.__logger.debug(
        #     f"==========> Transaction inserted: {tx_hash.hex()[-4:]}")
        network = self.get_network()
        network.broadcast_new_tx(tx, excludes=[sender])
        miner.receive_new_tx(tx)
