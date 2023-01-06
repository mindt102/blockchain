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
        txout, _, _ = data_to_txout(d)
        outputs.append(txout)
    return outputs


@ query_func
def get_txout_by_id(txout_id: int, db=None) -> tuple[TxOut, int, int]:
    """
    Get a transaction output by its id
    Returns:
        TxOut, tx_id, txout_index
    """
    data = db.selectOne(__tableName, "id", "*", (txout_id,))
    if not data:
        return None
    return data_to_txout(data)


@query_func
def get_txouts_by_addr(addr: str, db=None) -> list[TxOut]:
    data = db.selectAll(__tableName, where="addr", params=(addr,))
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
def get_utxo(addrs: list[str] = [], db=None) -> dict[tuple[bytes, int], TxOut]:
    query = f"""SELECT *
    FROM tx_outputs
    WHERE  {len(addrs)}=0 OR addr IN ({''.join([f"'{a}'," for a in addrs])[:-1]})
    EXCEPT
        SELECT txout.*
        FROM tx_outputs txout
        JOIN tx_inputs txin
        ON txout.id = txin.tx_output_id;
    """  # , 'AtMa6huHpUv3uPPpwqjLV3YaHp8GGQWA5'
    # __logger.debug(query)
    data = db.fetchAll(query)
    # __logger.debug(len(data))
    result = dict()
    if not data:
        return result

    from database.transaction_queries import get_tx_by_id

    for d in data:
        txout, tx_id, txout_index = data_to_txout(d)
        tx = get_tx_by_id(tx_id, db=db)
        if not tx:
            __logger.error("Transaction not found")
            raise Exception("Transaction not found")
        tx_hash = tx.get_hash()
        # __logger.debug(f"tx_hash: {tx_hash}, txout_index: {txout_index}")
        result[(tx_hash, txout_index)] = txout
    # __logger.debug(len(result))
    return result


@query_func
def get_txouts_by_addr(addr: str, db=None) -> list[TxOut]:
    query = f"""SELECT amount, txs.tx_hash, txs2.tx_hash, height, timestamp
FROM tx_outputs txouts 
LEFT OUTER JOIN tx_inputs txins
ON txouts.id = txins.tx_output_id
JOIN transactions txs 
ON txouts.tx_id = txs.id
LEFT OUTER JOIN transactions txs2
ON txins.tx_id = txs2.id
JOIN block_headers headers
ON txs.block_header_id = headers.id
WHERE addr = '{addr}'
ORDER BY timestamp DESC;
"""
    data = db.fetchAll(query)
    results = []
    for d in data:
        (amount, received_tx, spent_tx, block, timestamp) = d
        results.append(
            {
                "amount": amount,
                "received_tx": received_tx.hex(),
                "spent_tx": spent_tx.hex() if spent_tx else None,
                "block": block,
                "timestamp": timestamp,
            }
        )
    return results


@query_func
def get_balance_by_addrs(addrs: list[str], db=None) -> int:
    if len(addrs) == 0:
        return 0
    query = f"""SELECT SUM(amount)
FROM tx_outputs txouts 
LEFT OUTER JOIN tx_inputs txins
ON txouts.id = txins.tx_output_id
WHERE addr IN ({''.join([f"'{a}'," for a in addrs])[:-1]})
AND txins.tx_output_id IS NULL;"""
    data = db.fetchOne(query)
    if not data:
        return 0
    return data[0]


def data_to_txout(data: tuple) -> tuple[TxOut, int, int]:
    '''
    Returns TxOut, tx_id, txout_index
    '''
    txout_id, tx_id, txout_index, amount, locking_script, addr = data
    return TxOut(amount, Script.parse(locking_script)[0], addr), tx_id, txout_index
