from blockchain.Block import Block
from blockchain.Blockchain import Blockchain
from blockchain.BlockHeader import BlockHeader
from blockchain.const import (DIFFICULTY_ADJUSTMENT_INTERVAL,
                              EXPECTED_MINE_TIME, INITIAL_BITS, REWARD)
from blockchain.Script import Script
from blockchain.Transaction import Transaction
from blockchain.TxIn import TxIn
from blockchain.TxOut import TxOut
from utils import get_logger

__logger = get_logger(__name__)

blockchain = Blockchain()

__logger.info("Blockchain initialized.")
