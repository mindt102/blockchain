from typing import Self

from blockchain.TxIn import TxIn
from blockchain.TxOut import TxOut


class Transaction:
    def __init__(self, inputs: list[TxIn] = [], outputs: list[TxOut] = []) -> None:
        self.inputs = inputs
        self.outputs = outputs

    def __repr__(self) -> str:
        return f'''
Transaction(
    inputs={self.inputs}, 
    outputs={self.outputs}
)'''

    def serialize(self) -> bytes:
        inputs_bytes = b''.join([txin.serialize() for txin in self.inputs])
        outputs_bytes = b''.join([txout.serialize() for txout in self.outputs])
        return len(self.inputs).to_bytes(4, 'little') + inputs_bytes + len(self.outputs).to_bytes(4, 'little') + outputs_bytes

    @classmethod
    def parse(cls, stream: bytes) -> tuple[Self, bytes]:
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
