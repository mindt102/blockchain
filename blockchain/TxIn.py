
from blockchain.Script import Script


class TxIn:
    def __init__(self, prev_tx: bytes, output_index: int, unlocking_script: Script) -> None:
        self.prev_tx = prev_tx
        self.output_index = output_index
        self.unlocking_script = unlocking_script

    def serialize(self) -> bytes:
        return self.prev_tx + self.output_index.to_bytes(4, 'little') + self.unlocking_script.serialize()

    def __repr__(self) -> str:
        return f'''TxIn(
    prev_tx={self.prev_tx},
    output_index={self.output_index},
    unlocking_script={self.unlocking_script}
)'''

    @classmethod
    def parse(cls, stream: bytes) -> tuple['TxIn', bytes]:
        prev_tx = stream[:32]
        stream = stream[32:]
        output_index = int.from_bytes(stream[:4], 'little')
        stream = stream[4:]
        unlocking_script, stream = Script.parse(stream)
        return cls(prev_tx, output_index, unlocking_script), stream
