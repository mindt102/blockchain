from flask import Blueprint
from flask_paginate import get_page_args

from network import network
from blockchain import blockchain
from Miner import miner
import utils
_logger = utils.get_logger(__name__)

blueprint = Blueprint('node', __name__, url_prefix='/node')


@blueprint.route('/status')
def get_node_status():
    return {
        "network_ready": network.is_ready(),
        "blockchain_ready": blockchain.is_ready(),
    }, 200


@blueprint.route('/peers')
def get_peers():
    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page')
    peers = [peer.to_json() for peer in network.get_peers().values()]
    total = len(peers)
    results = peers[offset:offset + per_page]
    return {"total": total,
            "peers": results}


@blueprint.route('/mempool')
def get_mempool():
    results = []
    txs = miner.get_mempool()
    for tx in txs:
        tx_json = tx.to_json()
        if not tx.is_coinbase():
            prev_outputs = tx.get_prev_outputs()
            for i, prev_tx_output in enumerate(prev_outputs):
                tx_json["inputs"][i]["prev_output"] = prev_tx_output.to_json()
        results.append(tx_json)
    return results, 200


@blueprint.route('/candidate_block')
def get_candidate_block():
    return miner.get_candidate_block().to_json(), 200
