from blockchain.Block import Block
from database.DatabaseController import query_func
from database.BlockHeaderTable import get_header_by_hash, insert_header
from database.TransactionTable import get_tx_by_header, insert_tx


@query_func
def insert_block(block: Block, db=None):
    print(block)
    header_id = insert_header(block.get_header(), db=db)
    for index, tx in enumerate(block.get_transactions()):
        insert_tx(tx, header_id, index, db=db)


@query_func
def get_block_by_hash(block_hash: bytes, db=None) -> Block:
    header_id, header = get_header_by_hash(block_hash)
    if not header:
        return None
    txs = get_tx_by_header(header_id)
    block = Block(transactions=txs, header=header)
    print(block)
    return block


@query_func
def get_latest_block(db=None) -> Block:
    pass


@query_func
def get_utxo_set(db=None) -> dict:
    pass
