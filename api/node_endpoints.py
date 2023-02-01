from flask import Blueprint
from flask_paginate import get_page_args

import utils
from blockchain import blockchain
from Miner import miner
from network import network

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
    results = [tx.to_json() for tx in txs]
    return results, 200


@blueprint.route('/candidate_block')
def get_candidate_block():
    return miner.get_candidate_block().to_json(), 200
