import logging
import threading

from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO

import utils
from api.addr_endpoints import blueprint as addr_endpoint
from api.block_endpoints import blueprint as block_endpoint
from api.node_endpoints import blueprint as node_endpoint
from api.transaction_endpoints import blueprint as transaction_endpoint

_logger = utils.get_logger(__name__)
app = Flask(__name__)

CORS(app)

app.register_blueprint(block_endpoint)
app.register_blueprint(transaction_endpoint)
app.register_blueprint(addr_endpoint)
app.register_blueprint(node_endpoint)

socketio = SocketIO(app, cors_allowed_origins="*")
logging.getLogger("socketio").setLevel(logging.ERROR)
logging.getLogger('werkzeug').setLevel(logging.ERROR)


def emit_event(event: str, data: dict = None):
    socketio.emit(event, data, broadcast=True)


@socketio.on("connect")
def connect():
    session_id = request.sid
    _logger.info(f"Client {session_id} connected")
    emit_event(f"Client {session_id} connected")


api_thread = threading.Thread(target=lambda: socketio.run(
    app,
    host="0.0.0.0",
    port=3000,
    debug=True,
    use_reloader=False,
    allow_unsafe_werkzeug=True,
    log_output=False
), daemon=True)
