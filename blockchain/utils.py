from database.DatabaseController import DatabaseController


def getTxByHash(txHash: bytes):
    __db = DatabaseController()
    tx = __db.selectOne('transactions', "tx_hash", "*", params=(txHash,))
    print(txHash.hex())
    if tx:
        return tx[0]
    return None
