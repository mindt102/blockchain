from flask import Blueprint
from flask_paginate import get_page_args
from flask_restful import reqparse

import database
import utils
import wallet
from blockchain import blockchain
from utils.hashing import decode_base58check

_logger = utils.get_logger(__name__)

blueprint = Blueprint('transaction', __name__, url_prefix='/transactions')


@blueprint.route('/<string:tx_hash>')
def get_transaction(tx_hash):
    try:
        tx_hash_bytes = bytes.fromhex(tx_hash)
    except:
        _logger.warning(f"Invalid hash {tx_hash}")
        return {"message": "Invalid hash"}, 404

    tx, block_header_id = database.get_tx_by_hash(tx_hash_bytes)
    if not tx:
        return {"message": "Transaction not found"}, 404
    result = tx.to_json()
    result["block"] = database.get_height_by_id(block_header_id)
    return result, 200


@blueprint.route('/block/<int:height>')
def get_transactions(height):
    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page')

    block = database.get_block_by_height(height=height)
    if not block:
        return {"message": "Block not found"}, 404
    txs = block.get_transactions()[offset:offset + per_page]
    results = [tx.to_json() for tx in txs]
    return results, 200


@blueprint.route('', methods=['POST'])
def create_transaction():
    create_tx_argparser = reqparse.RequestParser()
    create_tx_argparser.add_argument(
        "amount", type=int, help="Amount of coin to send", required=True)
    create_tx_argparser.add_argument(
        "receiver", type=str, help="Address of the receiver", required=True)
    args = create_tx_argparser.parse_args()

    amount = args["amount"]
    receiver = args["receiver"]
    try:
        decode_base58check(receiver)
    except:
        _logger.warning(f"Invalid address: {receiver}")
        return {"message": "Invalid address"}, 400
    try:
        tx = wallet.create_transaction(receiver, amount)
        tx_hash = tx.get_hash().hex()
        _logger.info(f"Created transaction: {tx_hash[:4]}...{tx_hash[-4:]}")
        blockchain.receive_new_tx(tx)
        return tx.to_json(), 201
    except (AssertionError, ValueError) as e:
        return {"message": str(e)}, 400
    except Exception as e:
        _logger.exception(f"Failed to create transaction: {e}")
        return {"message": "Failed to create transaction"}, 500
