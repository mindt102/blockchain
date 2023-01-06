# import os
# import threading
# import time

# from ellipticcurve.ecdsa import Ecdsa
# from ellipticcurve.privateKey import PrivateKey
# from ellipticcurve.publicKey import PublicKey
# import database

# import utils
# from blockchain import Script, Transaction, TxIn, TxOut
# from Role import Role
# from utils import encode_base58check, hash160

# # from api import app
# from utils.hashing import decode_base58check


# class Wallet(Role):
#     '''Provide wallet functionality'''
#     __logger = utils.get_logger(__name__)

#     __privkey_file = "privkey.pem"

#     __privkey: PrivateKey = None
#     __pubkey: PublicKey = None
#     __addr: str = None

#     def __init__(self, *args, **kwargs):
#         # self.wallet = self
#         # self.__privkey_file = "privkey.pem"
#         self.__init_privkey()
#         self.__init_addr()
#         # super().__init__(wallet=self, *args, **kwargs)
#         super().__init__(*args, **kwargs)

#     @classmethod
#     def __init_privkey(cls):
#         '''
#         Initialize private key
#         Create a new private key if one does not exist
#         Else load the existing private key
#         '''
#         if os.path.exists(cls.__privkey_file):
#             with open(cls.__privkey_file, "r") as f:
#                 cls.__privkey = PrivateKey.fromPem(f.read())
#         else:
#             cls.__privkey = cls.generate_privkey()
#             with open(cls.__privkey_file, "w") as f:
#                 f.write(cls.__privkey.toPem())

#     @classmethod
#     def __init_addr(cls):
#         '''
#         Generate address from public key
#         '''
#         cls.__pubkey = cls.__privkey.publicKey()
#         pubkey = cls.__pubkey.toCompressed().encode()
#         pubkeyhash = hash160(pubkey)
#         cls.__addr = encode_base58check(pubkeyhash)

#     @classmethod
#     def get_privkey(cls):
#         return cls.__privkey

#     @classmethod
#     def get_pubkey(cls):
#         return cls.__pubkey

#     @classmethod
#     def get_addr(cls):
#         return cls.__addr

#     @classmethod
#     def generate_privkey(cls):
#         return PrivateKey()

#     @classmethod
#     def create_transaction(cls, to_addr: str, amount: int):
#         '''Create a transaction to send coins to another address'''
#         # blockchain: Blockchain = cls.get_blockchain()
#         # utxo_sets = blockchain.get_UTXO_set()
#         try:
#             decode_base58check(to_addr)
#         except:
#             cls.__logger.exception(f"Invalid address: {to_addr}")
#             raise
#         utxo_sets = database.get_utxo()
#         selected_utxo = cls.select_utxo(amount, utxo_sets)
#         inputs: list[TxIn] = []
#         total_input = 0
#         for key, utxo in selected_utxo.items():
#             prev_hash, index = key
#             tx_in = TxIn(prev_hash, index)
#             inputs.append(tx_in)
#             total_input += utxo.get_amount()
#         change = total_input - amount
#         assert change >= 0
#         change_output = TxOut(change, addr=cls.get_addr())
#         spending_output = TxOut(amount, addr=to_addr)
#         outputs: list[TxOut] = [change_output, spending_output]

#         tx = Transaction(inputs, outputs)
#         cls.sign_transaction(tx)
#         return tx

#     @classmethod
#     def sign_transaction(cls, tx: Transaction):
#         '''Sign a transaction'''
#         signature = Ecdsa.sign(tx.get_signing_data(),
#                                cls.get_privkey()).toDer()
#         pubkey = cls.get_pubkey().toCompressed().encode()
#         unlocking_script = Script.get_unlock(signature, pubkey)
#         tx.set_unlocking_script(unlocking_script)

#     @classmethod
#     def select_utxo(cls, amount: int, utxo_set: dict[tuple[bytes, int], TxOut]) -> dict[tuple[bytes, int], TxOut]:
#         '''Select UTXO to spend. utxo_set is a dict with key: (prev_hash, output_index) and value: TxOut'''
#         total = 0
#         selected_utxo = dict()

#         for key, value in utxo_set.items():
#             coin = value.get_amount()
#             selected_utxo[key] = value
#             total += coin
#             if total >= amount:
#                 return selected_utxo
#         raise ValueError(f"Not enough coin. Current balance: {total}")

#     def run(self):
#         '''Run the wallet'''
#         self.__logger.info("Wallet is listening on port http://localhost:5000")
#         self.__start_app()
#         while self.active():
#             time.sleep(.1)

#     def __start_app(self):
#         self.__api_thread = threading.Thread(target=lambda: app.run(
#             host="127.0.0.1", port=5000, debug=True, use_reloader=False
#         ))
#         self.__api_thread.setDaemon(True)
#         self.__api_thread.start()
