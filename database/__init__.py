import json
import os

from blockchain import Block
from database.block_header_queries import (get_bits_by_height,
                                           get_header_by_hash,
                                           get_header_by_height,
                                           get_height_by_id, get_max_height,
                                           get_top_header, insert_header)
from database.block_queries import (get_block_by_hash, get_block_by_height,
                                    get_blocks_by_height, get_top_block,
                                    insert_block)
from database.DatabaseController import DatabaseController
from database.generateQuery import GenerateQuery
from database.transaction_queries import (get_tx_by_hash,
                                          get_txhistory_by_addr, insert_tx)
from database.txin_queries import insert_txin
from database.txout_queries import (get_balance_by_addrs, get_txout_by_tx,
                                    get_txout_id, get_txouts_by_addr, get_utxo,
                                    insert_txout)
from utils import config, get_logger

__logger = get_logger(__name__)

genesis_block_path = config["db"]["genesis_block_path"]


def create_db(config: dict, genesis_block: Block):
    db_file = config["name"]
    if os.path.exists(db_file) and not config["reset"]:
        return
    __logger.info("Resetting database...")
    if os.path.exists(db_file):
        os.remove(db_file)
    db = DatabaseController()
    with open(config["sample"]) as f:
        tables_config = json.loads(f.read())
        create_queries = map(
            lambda conf: GenerateQuery(**conf), tables_config)
        for query in create_queries:
            db.execute(str(query))
    insert_block(genesis_block, height=0, db=db)


with open(genesis_block_path, 'rb') as f:
    try:
        genesis_block = Block.parse(f.read())[0]
        create_db(config["db"], genesis_block)
        __logger.info("Database initialized.")
    except Exception:
        __logger.exception("Fail to initialize database.")
        raise
