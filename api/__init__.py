from flask import Flask
from flask_cors import CORS

# from api.BlockApi import BlockApi, BlocksApi
# from api.TransactionApi import TransactionApi, TransactionHashApi, TransactionBlockApi
# from api.AddrApi import AddrApi
from api.block_endpoints import blueprint as block_endpoint
from api.transaction_endpoints import blueprint as transaction_endpoint
from api.addr_endpoints import blueprint as addr_endpoint

app = Flask(__name__)

CORS(app)


app.register_blueprint(block_endpoint)
app.register_blueprint(transaction_endpoint)
app.register_blueprint(addr_endpoint)

# api = Api(app)

# Apis = [
#     # BlockApi,
#     # BlocksApi,
#     TransactionApi,
#     TransactionHashApi,
#     TransactionBlockApi,
#     AddrApi,
# ]

# for Api in Apis:
#     api.add_resource(Api, Api.route)
