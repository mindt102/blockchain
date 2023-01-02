from database.DatabaseController import query_func
from database.txin_queries import insert_txin, get_txin_by_tx
from database.txout_queries import insert_txout, get_txout_by_tx
from blockchain.Transaction import Transaction
from utils import get_logger

__tableName = "transactions"
__tableCol = [
    "block_header_id",
    "tx_hash",
    "tx_index",
]
__logger = get_logger(__name__)


@query_func
def get_tx_by_hash(tx_hash: bytes, db=None) -> tuple[Transaction, int]:
    tx_data = db.selectOne(__tableName, "tx_hash", "*", params=(tx_hash,))
    if tx_data:
        return data_to_tx(tx_data, db=db)
    return None, None


@query_func
def get_txs_by_header(header_id: int, db=None) -> list[Transaction]:
    # tx_data = db.selectOne(__tableName, "id", "*", values=(header_id,))
    data = db.selectAll(__tableName, where="block_header_id",
                        sortby="tx_index", params=(header_id,))
    if not data:
        __logger.debug("No transactions found")
        return []
    txs = []
    for tx_data in data:
        tx, _ = data_to_tx(tx_data, db=db)
        txs.append(tx)
    return txs


@query_func
def get_tx_by_id(tx_id: int, db=None) -> Transaction:
    tx_data = db.selectOne(__tableName, "id", "*", params=(tx_id,))
    if tx_data:
        tx, _ = data_to_tx(tx_data, db=db)
        return tx
    return None


@query_func
def get_txhash_by_id(tx_id: int, db=None) -> Transaction:
    tx_data = db.selectOne(__tableName, "id", "tx_hash", params=(tx_id,))
    if tx_data:
        tx_hash = tx_data[0]
        return tx_hash
    return None


def get_txid_by_hash(tx_hash: bytes, db=None) -> int:
    tx_data = db.selectOne(__tableName, "tx_hash", "id", params=(tx_hash,))
    if tx_data:
        tx_id = tx_data[0]
        return tx_id
    return None


@query_func
def insert_tx(tx: Transaction, header_id: int, tx_index: int, db=None):
    values = (
        header_id,
        tx.get_hash(),
        tx_index
    )
    txid = db.insert(__tableName, __tableCol, values)
    for index, txout in enumerate(tx.get_outputs()):
        # txout.insert(txId, index)
        insert_txout(txout=txout, txid=txid, index=index, db=db)

    for index, txin in enumerate(tx.get_inputs()):
        # if not tx.is_coinbase():
        prev_tx_id = get_txid_by_hash(txin.get_prev_tx_hash(), db=db)
        insert_txin(txin=txin, txid=txid, index=index, prev_tx_id=prev_tx_id,
                    is_coinbase=tx.is_coinbase(), db=db)
        # __logger.debug(f"Inserted txin: {txin}")


def data_to_tx(tx_data: tuple, db=None) -> tuple[Transaction, int]:
    txid = tx_data[0]
    block_header_id = tx_data[1]
    outputs = get_txout_by_tx(txid, db=db)
    inputs = get_txin_by_tx(txid, db=db)
    return Transaction(inputs=inputs, outputs=outputs), block_header_id
