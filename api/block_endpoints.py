from flask import Blueprint, jsonify
from flask_paginate import get_page_args

import database

blueprint = Blueprint('block', __name__, url_prefix='/blocks')


@blueprint.route('/<int:block_height>')
def get_block(block_height):
    block = database.get_block_by_height(block_height)
    if not block:
        return {"message": "Block not found"}, 404
    return block.to_json(), 200


@blueprint.route('/')
def get_blocks():
    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page')

    blocks = database.get_blocks_by_height(offset, offset + per_page)
    total = database.get_max_height() + 1
    results = []
    for block in blocks:
        data = block.get_header().to_json()
        txs = block.get_transactions()
        first_tx = txs[0]
        data["miner"] = first_tx.get_outputs()[0].get_addr()
        data["tx_count"] = len(txs)
        results.append(data)
    return {"total": total,
            "blocks": results}
