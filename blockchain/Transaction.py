from ellipticcurve.ecdsa import Ecdsa

from blockchain import Script
from blockchain.TxIn import TxIn
from blockchain.TxOut import TxOut
# import database
# from database.DatabaseController import DatabaseController
from utils import encode_base58, hash256


class Transaction:
    def __init__(self, inputs: list[TxIn] = [], outputs: list[TxOut] = []) -> None:
        self.__inputs = inputs
        self.__outputs = outputs

    def __repr__(self) -> str:
        return f'''Transaction(
    inputs={self.__inputs},
    outputs={self.__outputs}
)'''

    def sign(self, priv_key) -> None:
        empty_inputs = [txin.get_empty_copy() for txin in self.__inputs]
        empty_tx = Transaction(empty_inputs, self.__outputs)
        signature = Ecdsa.sign(encode_base58(
            hash256(empty_tx.serialize())), priv_key)
        return signature.toDer()

    def set_unlocking_script(self, unlocking_script: Script) -> None:
        for txin in self.__inputs:
            txin.set_unlocking_script(unlocking_script)

    def serialize(self) -> bytes:
        inputs_bytes = b''.join([txin.serialize() for txin in self.__inputs])
        outputs_bytes = b''.join([txout.serialize()
                                 for txout in self.__outputs])
        return len(self.__inputs).to_bytes(4, 'little') + inputs_bytes + len(self.__outputs).to_bytes(4, 'little') + outputs_bytes

    @classmethod
    def parse(cls, stream: bytes) -> tuple['Transaction', bytes]:
        num_inputs = int.from_bytes(stream[:4], 'little')
        stream = stream[4:]
        inputs = []
        for _ in range(num_inputs):
            txin, stream = TxIn.parse(stream)
            inputs.append(txin)

        num_outputs = int.from_bytes(stream[:4], 'little')
        stream = stream[4:]
        outputs = []
        for _ in range(num_outputs):
            txout, stream = TxOut.parse(stream)
            outputs.append(txout)

        return cls(inputs, outputs), stream

    def get_hash(self) -> bytes:
        return hash256(self.serialize())

    def get_outputs(self) -> list[TxOut]:
        return self.__outputs

    def get_output_by_index(self, output_index: int) -> list[TxOut]:
        return self.__outputs[output_index]

    def get_inputs(self) -> list[TxIn]:
        return self.__inputs

    def get_empty_copy(self) -> 'Transaction':
        return Transaction([txin.get_empty_copy() for txin in self.__inputs], self.__outputs)

    # def get_prev_tx(self) -> TxIn:
    #     tx = self.__inputs
    #     return tx[0].get_prev_hash()

    def get_signing_data(self) -> bytes:
        empty_tx = self.get_empty_copy()
        return encode_base58(
            hash256(empty_tx.serialize()))

    def is_coinbase(self):
        inputs = self.get_inputs()
        # tx = block.get_transactions()
        if len(inputs) != 1:
            return False

        first_input = inputs[0]
        prev_tx = first_input.get_prev_tx_hash()
        output_index = first_input.get_output_index()

        if prev_tx != b'\x00' * 32 or output_index != 0xffffffff:
            return False

        return True

    # __tableName = "transactions"
    # __tableCol = ["block_header_id", "tx_hash"]

    # def insert(self, blockHeaderId: int):
    #     values = (blockHeaderId, self.get_hash())
    #     __db = DatabaseController()
    #     txId = __db.insert(self.__tableName, self.__tableCol, values)
    #     for idx, txOut in enumerate(self.get_outputs()):
    #         # txOut.insert(txId, idx)
    #         database.insert_txout(txout=txOut, txid=txId, index=idx, db=__db)

    #     for idx, txIn in enumerate(self.get_inputs()):
    #         if not self.is_coinbase():
    #             txIn.insert()
    #             database.insert_txin(txin=txIn, db=__db)
