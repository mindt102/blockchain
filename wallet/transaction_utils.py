from ellipticcurve.ecdsa import Ecdsa

from blockchain.Script import Script
from blockchain.Transaction import Transaction
from blockchain.TxIn import TxIn
from blockchain.TxOut import TxOut
from utils import decode_base58check, get_logger
from wallet.key_utils import address, privkey, pubkey

__logger = get_logger(__name__)


def create_transaction(to_addr: str, amount: int, change_addr: str = address):
    '''Create a transaction to send coins to another address'''
    try:
        decode_base58check(to_addr)
        decode_base58check(change_addr)
    except:
        __logger.exception(f"Invalid address: {to_addr}")
        raise
    from blockchain import blockchain
    utxo_sets = blockchain.get_utxo(addrs=[address])
    selected_utxo = select_utxo(amount, utxo_sets)
    inputs: list[TxIn] = []
    total_input = 0
    for key, utxo in selected_utxo.items():
        prev_hash, index = key
        tx_in = TxIn(prev_hash, index)
        inputs.append(tx_in)
        total_input += utxo.get_amount()
    change = total_input - amount
    assert change >= 0
    spending_output = TxOut(amount, addr=to_addr)
    outputs: list[TxOut] = [spending_output]
    if change > 0:
        change_output = TxOut(change, addr=change_addr)
        outputs.append(change_output)
    tx = Transaction(inputs, outputs)
    # sign_transaction(tx)
    tx.sign(privkey, pubkey)
    return tx


# def sign_transaction(tx: Transaction, privkey=privkey, pubkey=pubkey):
#     '''Sign a transaction'''
#     # print(f"Signing data: {tx.get_signing_data()}")
#     # signature = Ecdsa.sign(tx.get_signing_data(),
#     #                        privkey).toDer()
#     tx.sign(privkey)
#     # print(f"Signature: {signature}")
#     # print(f"Private key: {privkey.toPem()}")
#     pubkey = pubkey.toCompressed().encode()
#     unlocking_script = Script.get_unlock(signature, pubkey)
#     tx.set_unlocking_script(unlocking_script)


def select_utxo(amount: int, utxo_set: dict[tuple[bytes, int], TxOut]) -> dict[tuple[bytes, int], TxOut]:
    '''Select UTXO to spend. utxo_set is a dict with key: (prev_hash, output_index) and value: TxOut'''
    total = 0
    selected_utxo = dict()

    for key, value in utxo_set.items():
        coin = value.get_amount()
        selected_utxo[key] = value
        total += coin
        if total >= amount:
            return selected_utxo
    __logger.warning(f"Not enough coin. Current balance: {total}")
    raise ValueError(f"Not enough coin. Current balance: {total}")
