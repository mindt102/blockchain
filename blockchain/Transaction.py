from ellipticcurve.ecdsa import Ecdsa
from blockchain import Script
from blockchain import Blockchain
from blockchain.TxIn import TxIn
from blockchain.TxOut import TxOut
from utils import hash256, encode_base58


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

    def get_signing_data(self) -> bytes:
        empty_tx = self.get_empty_copy()
        return encode_base58(
            hash256(empty_tx.serialize()))

    #Hung & Hien in processing

    def checkspentness_Inputs(self, addr=[]):
        UTXOs = Blockchain.get_UTXO_set(addr)
        inputs = self.get_inputs(addr)
        for _ in inputs:
            for key, value in UTXOs.items():
                if _ == value:
                    return "Valid block"
            return "Invalid or spent block"

    def check_sumIN_OUT(self, stream: bytes):
        Txin, Txout, Stream = self.parse(stream)
        if sum(TxIn) > sum(TxOut): return "Create money"
        else: return "Overflow Incident" 
