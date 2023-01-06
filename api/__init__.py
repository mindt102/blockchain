import threading
from flask import Flask
from flask_cors import CORS

from api.addr_endpoints import blueprint as addr_endpoint
from api.block_endpoints import blueprint as block_endpoint
from api.node_endpoints import blueprint as node_endpoint
from api.transaction_endpoints import blueprint as transaction_endpoint

app = Flask(__name__)

CORS(app)

app.register_blueprint(block_endpoint)
app.register_blueprint(transaction_endpoint)
app.register_blueprint(addr_endpoint)
app.register_blueprint(node_endpoint)

api_thread = threading.Thread(target=lambda: app.run(
    host="0.0.0.0", port=3000, debug=True, use_reloader=False
), daemon=True)
