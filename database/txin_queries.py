from blockchain.Script import Script
from blockchain.TxIn import TxIn
from blockchain.TxOut import TxOut
from database.DatabaseController import query_func
from database.txout_queries import get_txout_by_id, get_txout_by_tx, get_txout_id
from utils import get_logger

__tableName = "tx_inputs"
__tableCol = [
    "tx_id",
    "txin_index",
    "tx_output_id",
    "unlocking_script"
]
__logger = get_logger(__name__)


@query_func
def insert_txin(txin: TxIn, txid: int, index: int, prev_tx_id: int, is_coinbase: bool = False, db=None):
    if not is_coinbase:
        txout_id = get_txout_id(prev_tx_id, txin.get_output_index())
        if not txout_id:
            __logger.warning("Transaction output not found")
    else:
        txout_id = None
    values = (
        txid,
        index,
        txout_id,
        txin.get_unlocking_script().serialize(),
    )
    return db.insert(__tableName, __tableCol, values)


@query_func
def get_txin_by_tx(txid: int, db=None) -> list[TxIn]:
    data = db.selectAll(__tableName, where="tx_id",
                        sortby="txin_index", params=(txid,))
    if not data:
        __logger.warning("No transaction inputs found")
        return []
    inputs = []
    for d in data:
        inputs.append(data_to_txin(d))
    return inputs


def data_to_txin(data: tuple) -> TxIn:
    _, _, txout_id, unlocking_script_raw = data
    unlocking_script, _ = Script.parse(unlocking_script_raw)
    if not txout_id:
        prev_tx_hash = 32 * b"\x00"
        output_index = 0xffffffff
        return TxIn(prev_tx_hash, output_index, unlocking_script)

    txout, tx_id, output_index = get_txout_by_id(txout_id)
    if not txout:
        raise Exception("Transaction output not found")
    from database.transaction_queries import get_txhash_by_id
    prev_tx_hash = get_txhash_by_id(tx_id)
    # output_index = txout.get_index()
    return TxIn(prev_tx_hash, output_index, unlocking_script)
