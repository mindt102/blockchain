
from blockchain.Script import Script


class TxOut:
    def __init__(self, amount: int, locking_script: Script) -> None:
        self.amount = amount
        self.locking_script = locking_script

    def serialize(self) -> bytes:
        return self.amount.to_bytes(8, 'little') + self.locking_script.serialize()

    def __repr__(self) -> str:
        return f'''TxOut(
    amount={self.amount},
    locking_script={self.locking_script}
)'''

    @classmethod
    def parse(cls, stream: bytes) -> tuple['TxOut', bytes]:
        amount = int.from_bytes(stream[:8], 'little')
        stream = stream[8:]
        locking_script, stream = Script.parse(stream)
        return cls(amount, locking_script), stream
