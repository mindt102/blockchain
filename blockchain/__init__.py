from blockchain.Block import Block
from blockchain.Blockchain import Blockchain
from blockchain.BlockHeader import BlockHeader
from blockchain.Script import Script
from blockchain.Transaction import Transaction
from blockchain.TxIn import TxIn
from blockchain.TxOut import TxOut
from utils import config, get_logger

__logger = get_logger(__name__)

blockchain = Blockchain(
    config=config["blockchain"],
    db_config=config["db"]
)
__logger.info("Blockchain initialized.")
