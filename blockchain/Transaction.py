from ellipticcurve.ecdsa import Ecdsa

from blockchain.Script import Script
from blockchain.TxIn import TxIn
from blockchain.TxOut import TxOut
# import database
# from database.DatabaseController import DatabaseController
from utils import encode_base58, hash256, get_logger


class Transaction:
    __logger = get_logger(__name__)

    def __init__(self, inputs: list[TxIn] = [], outputs: list[TxOut] = []) -> None:
        self.__inputs = inputs
        self.__outputs = outputs

    def to_json(self) -> dict:
        result = {
            'hash': self.get_hash().hex(),
            'inputs': [txin.to_json() for txin in self.__inputs],
            'outputs': [txout.to_json() for txout in self.__outputs]
        }
        # Include previous output for each input
        if not self.is_coinbase():
            import database
            for i, txin in enumerate(self.get_inputs()):
                prev_tx_hash = txin.get_prev_tx_hash()
                output_index = txin.get_output_index()

                prev_tx, _ = database.get_tx_by_hash(prev_tx_hash)
                if not prev_tx:
                    self.__logger.critical(
                        f"Transaction {self.get_hash()} has invalid input {txin}")

                prev_tx_output = prev_tx.get_outputs()[output_index]
                result['inputs'][i]['prev_output'] = prev_tx_output.to_json()
        return result

    def __repr__(self) -> str:
        return f'''Transaction({self.to_json()})'''

    def set_unlocking_script(self, unlocking_script: Script) -> None:
        for txin in self.__inputs:
            txin.set_unlocking_script(unlocking_script)

    def get_unlocking_script(self) -> Script:
        return self.__inputs[0].get_unlocking_script()

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
        # empty_tx = self.get_empty_copy()
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

    def sign(self, privkey, pubkey) -> None:
        signature = Ecdsa.sign(self.get_signing_data(), privkey).toDer()
        pubkey = pubkey.toCompressed().encode()
        self.set_unlocking_script(Script([signature, pubkey]))

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
