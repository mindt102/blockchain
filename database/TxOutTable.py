from database.DatabaseController import query_func
from blockchain.TxOut import TxOut
from blockchain.Script import Script
from utils import get_logger
__tableName = "tx_outputs"
__tableCol = [
    "tx_id",
    "txout_index",
    "amount",
    "locking_script",
    "addr",
]
__logger = get_logger(__name__)


@query_func
def get_txout_id(txId: int, txIndex: int, db=None) -> int:
    txOut = db.selectOne(
        __tableName, "tx_id,txout_index", "*", (txId, txIndex))
    if not txOut:
        raise Exception("Transaction output not found")
    return txOut[0]


@query_func
def get_txout_by_tx(txId: int, db=None) -> list[TxOut]:
    # query = f"SELECT * FROM {__tableName} WHERE tx_id = ? SORT BY index"
    # data = db.fetchAll(query, (txId,))
    data = db.selectAll(__tableName, where="tx_id",
                        sortby="txout_index", params=(txId,))
    if not data:
        __logger.debug("Transaction output not found")
        return []

    outputs = []
    for d in data:
        outputs.append(data_to_txout(d))
    return outputs


@ query_func
def get_txout_by_id(txOutId: int, db=None) -> TxOut:
    data = db.selectOne(__tableName, "id", "*", (txOutId,))
    if not data:
        return None
    return data_to_txout(data)


@ query_func
def insert_txout(txout: TxOut, txid: int, index: int, db=None):
    values = (
        txid,
        index,
        txout.get_amount(),
        txout.get_locking_script().serialize(),
        txout.get_addr(),
    )
    return db.insert(__tableName, __tableCol, values)


@query_func
def get_utxo(addr: str, db=None) -> list[TxOut]:
    query = f"""SELECT * 
    FROM tx_outputs 
    WHERE addr in ('9o9kCNjtdtfwF8gueroP6HMBF67PBjpjQ') 
    EXCEPT 
        SELECT txout.* 
        FROM tx_outputs txout  
        JOIN tx_inputs txin 
        ON txout.id = txin.tx_output_id;
    """  # , 'AtMa6huHpUv3uPPpwqjLV3YaHp8GGQWA5'
    data = db.fetchAll(query)
    if not data:
        return []
    return list(map(data_to_txout, data))


def data_to_txout(data: tuple) -> TxOut:
    _, _, _, amount, locking_script, addr = data
    return TxOut(amount, Script.parse(locking_script)[0], addr)
