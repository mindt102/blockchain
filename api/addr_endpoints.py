from flask_restful import Resource
from flask_paginate import get_page_args
from flask import Blueprint

import database
import utils
from wallet import address

_logger = utils.get_logger(__name__)
blueprint = Blueprint('addr', __name__, url_prefix='/addr')


@blueprint.route('/me')
def get_addr():
    return [address], 200


@blueprint.route('/history/<string:addr>')
def get_addr_history(addr):
    if addr == "me":
        addr = address
    txouts = database.get_txouts_by_addr(addr)
    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page')
    results = txouts[offset:offset + per_page]
    return {"address": addr, "txouts": results}, 200


@blueprint.route('/balance/<string:addr>')
def get_addr_balance(addr):
    if addr == "me":
        addr = address
    balance = database.get_balance_by_addrs(addrs=[addr])
    return {"address": addr,
            "balance": balance}, 200
