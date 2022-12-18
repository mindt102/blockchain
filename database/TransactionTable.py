from database.DatabaseController import query_func
from database.TxInTable import insert_txin, get_txin_by_tx
from database.TxOutTable import insert_txout, get_txout_by_tx
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
def get_tx_by_hash(tx_hash: bytes, db=None):
    tx = db.selectOne(__tableName, "tx_hash", "*", params=(tx_hash,))
    if tx:
        return tx[0]
    return None


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
        txid = tx_data[0]
        outputs = get_txout_by_tx(txid, db=db)
        inputs = get_txin_by_tx(txid, db=db)
        txs.append(Transaction(inputs=inputs, outputs=outputs))
    return txs


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
        insert_txin(txin, txid, index, db=db)
