import queue

import database
from blockchain import Block, Transaction, TxIn, TxOut
from Miner import miner
from Role import Role
from utils import bits_to_target, get_logger, target_to_bits
from blockchain.validators import validate_transaction, validate_block


class Blockchain(Role):
    '''Provide blockchain functionality'''
    __logger = get_logger(__name__)

    def __init__(self) -> None:
        self.__orphan_blocks: dict[bytes, Block] = dict()
        self.__is_ready = False
        super().__init__()

    def run(self) -> None:
        while self.active():
            try:
                func, args, kwargs = self.q.get(timeout=self.q_timeout)
                func(*args, **kwargs)
            except queue.Empty:
                pass

    def get_bits_by_height(self, height: int) -> bytes:
        from blockchain import DIFFICULTY_ADJUSTMENT_INTERVAL, INITIAL_BITS, EXPECTED_MINE_TIME
        # return INITIAL_BITS  # TODO: remove this line
        if not DIFFICULTY_ADJUSTMENT_INTERVAL:
            return INITIAL_BITS
        if height < DIFFICULTY_ADJUSTMENT_INTERVAL:
            return INITIAL_BITS
        if (height % DIFFICULTY_ADJUSTMENT_INTERVAL) != 0:
            bits = database.get_bits_by_height(height - 1)
            if not bits:
                self.__logger.error(f"Can't get bits at height {height - 1}")
            return bits

        prev_interval_start_block = database.get_block_by_height(
            height - DIFFICULTY_ADJUSTMENT_INTERVAL)
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
            EXPECTED_MINE_TIME * DIFFICULTY_ADJUSTMENT_INTERVAL)

        self.__logger.debug(f"New target: {new_target:064x} - {new_target}")
        self.__logger.debug(
            f"Adjustment factor: {new_target / prev_interval_target:.4f}")

        initial_target = bits_to_target(INITIAL_BITS)
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
            f"Blockchain is ready. Current height: {database.get_max_height()}")

    def get_genesis_block(self) -> Block:
        return self.__genesis_block

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
        """
        Returns the first block hash in the locator hashes that is in the database.
        If no block hash is in the database, returns the genesis block hash.
        params:
            locator_hashes: list of block hashes to search for in order by height descending
        returns:
            first shared block hash
        """
        for block_hash in locator_hashes:
            if database.get_header_by_hash(block_hash):
                return block_hash
        return self.get_genesis_block().get_header().get_hash()

    def share_blocks_from_hash(self, common_block_hash: bytes) -> list[bytes]:
        """
        Returns a list of block hashes starting from the block after the common block hash.
        params:
            common_block_hash: the first block hash to return
        returns:
            list of block hashes
        """
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
        params:
            addrs: list of addresses to filter by
        returns:
            UTXO set from the database excluding spent outputs in mempool
        '''
        utxo_set = database.get_utxo(addrs)
        self.__logger.debug(f"UTXO set: {len(utxo_set)}")
        spent_set = miner.get_spent_txouts()
        self.__logger.debug(f"Spend set: {len(spent_set)}")
        for key in spent_set:
            utxo_set.pop(key, None)
        return utxo_set

    def validate_block_bits(self, bits: int, height: int) -> bool:
        return bits == self.get_bits_by_height(height=height)

    @ Role._rpc
    def receive_new_block(self, block: Block, sender: str = None) -> None:
        db = database.DatabaseController()
        header = block.get_header()
        block_hash = header.get_hash()

        # Check if block already exists
        existing_header, _, _ = database.get_header_by_hash(
            block_hash, db=db)
        if existing_header:
            return

        # Check if block is valid
        if not validate_block(block):
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
            f"Block {block_hash.hex()[-4:]} inserted at height {height}")

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
            del self.__orphan_blocks[parent_hash]
            parent_hash = orphan_hash

        if self.get_top_hash() == block_hash and self.__is_ready:
            from api import emit_event
            from network import network

            miner.receive_new_block()
            network.broadcast_new_block(block, excludes=[sender])
            emit_event("block", block.to_json())
        db.close()

    @ Role._rpc
    def receive_new_tx(self, tx: Transaction, sender: str = None) -> None:
        db = database.DatabaseController()
        tx_hash = tx.get_hash()
        if sender:  # If sender is not None, it means the transaction is received from other peers, else it is created by the node itself
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
        if not validate_transaction(tx):
            self.__logger.warning(f"Invalid transaction")
            return

        from network import network
        network.broadcast_new_tx(tx, excludes=[sender])
        miner.receive_new_tx(tx)
