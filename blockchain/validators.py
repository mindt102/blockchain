import database
import utils
from blockchain.Block import Block
from blockchain.Transaction import Transaction
from blockchain.TxIn import TxIn

_logger = utils.get_logger(__name__)


def verify_txin(txin: TxIn, signing_data: str, utxo_set: dict, spent_txouts: set) -> bool:
    '''Verify a transaction input'''
    # If the input transaction is not in the UTXO set, return False
    prev_tx = txin.get_prev_tx_hash()
    output_index = txin.get_output_index()
    if (prev_tx, output_index) not in utxo_set and (prev_tx, output_index) not in spent_txouts:
        _logger.warning("Input transaction not in UTXO set")
        return False

    # If the previous transaction does not exist, return False
    prev_tx, _ = database.get_tx_by_hash(prev_tx)
    if prev_tx is None:
        _logger.warning("Previous transaction does not exist")
        return False

    # If the output index is out of range, return False
    prev_outputs = prev_tx.get_outputs()
    if output_index >= len(prev_outputs):
        _logger.warning("Output index out of range")
        return False

    # If the signature is not valid, return False
    prev_output = prev_outputs[output_index]
    locking_script = prev_output.get_locking_script()
    unlocking_script = txin.get_unlocking_script()
    if not (unlocking_script + locking_script).evaluate(signing_data):
        _logger.warning("Signature is not valid")
        return False

    spent_txouts.add((prev_tx, output_index))
    return True


def validate_transaction(tx: Transaction) -> bool:
    utxo_set = database.get_utxo()
    inputs = tx.get_inputs()
    outputs = tx.get_outputs()
    signing_data = tx.get_signing_data()

    # Check if there are any inputs or outputs
    if len(inputs) == 0 or len(outputs) == 0:
        _logger.debug(
            f"Invalid input or output length: {len(inputs)} and {len(outputs)}")
        return False

    # Calculate total input amount
    input_sum = 0
    spent_txouts = set()
    for txin in inputs:
        index = txin.get_output_index()
        prevtx = txin.get_prev_tx_hash()
        key = (prevtx, index)

        # Evaluate the locking script of each input
        if not verify_txin(txin, signing_data, utxo_set, spent_txouts):
            _logger.warning(
                f"Invalid unlocking script. Txin: {txin}")
            return False

        # Not an unspent transaction outputs
        if key not in utxo_set:
            _logger.warning(f"Not an UTXO")
            return False
        input_sum += utxo_set[key].get_amount()

    # Calculate total output amount
    output_sum = 0
    for txout in outputs:
        output_sum += txout.get_amount()

    if input_sum < output_sum:
        _logger.info(
            f"Input sum={input_sum} smaller than output sum={output_sum}")
        return False

    return True


def validate_block(block: Block) -> bool:
    header = block.get_header()
    # Check block header hash
    if not header.check_hash():
        _logger.debug("Invalid header hash")
        return False

    txs = block.get_transactions()
    # Check first transaction is coinbase
    if not txs[0].is_coinbase():
        _logger.debug("First tx is not coinbase")
        return False

    # Check merkle root received vs computed
    block_merkle_root = block.compute_merkle_root()
    if block_merkle_root != block.get_header().get_merkle_root():
        _logger.debug("Invalid merkel root")
        return False

    # Check validity of transactions
    for i in range(1, len(txs)):
        tx = txs[i]
        if tx.is_coinbase():
            _logger.debug(f"Transaction #{i} is coinbase")
            return False
        if not validate_transaction(tx):
            _logger.debug("Invalid transaction")
            return False

    return True
