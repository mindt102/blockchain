from blockchain.Block import Block
from database.DatabaseController import query_func
from database.BlockHeaderTable import get_header_by_hash, insert_header, get_header_by_maxheight
from database.TransactionTable import get_txs_by_header, insert_tx


@query_func
def insert_block(block: Block, height=0, db=None):
    header_id = insert_header(block.get_header(), height=height, db=db)
    for index, tx in enumerate(block.get_transactions()):
        insert_tx(tx, header_id, index, db=db)


@query_func
def get_block_by_hash(block_hash: bytes, db=None) -> Block:
    header, header_id, _ = get_header_by_hash(block_hash)
    if not header:
        return None
    txs = get_txs_by_header(header_id)
    return Block(transactions=txs, header=header)


@query_func
def get_top_block(db=None) -> tuple[Block, int]:
    header, header_id, height = get_header_by_maxheight(db=db)
    if not header:
        raise Exception("No block in database")
    txs = get_txs_by_header(header_id)
    return Block(transactions=txs, header=header), height


@query_func
def get_block_by_height(height: int, db=None) -> Block:
    pass


@query_func
def get_utxo_set(db=None) -> dict:
    pass
