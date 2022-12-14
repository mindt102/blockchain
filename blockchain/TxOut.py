
from blockchain.Script import Script


class TxOut:
    def __init__(self, amount: int, locking_script: Script = None, addr: str = None) -> None:
        self.__amount = amount
        if not locking_script:
            locking_script = Script.get_lock(addr)

        self.__locking_script = locking_script
        self.__addr = addr

    def serialize(self) -> bytes:
        return self.__amount.to_bytes(8, 'little') + self.__locking_script.serialize()

    def __repr__(self) -> str:
        return f'''TxOut(
    amount={self.__amount},
    locking_script={self.__locking_script}
)'''

    @classmethod
    def parse(cls, stream: bytes) -> tuple['TxOut', bytes]:
        amount = int.from_bytes(stream[:8], 'little')
        stream = stream[8:]
        locking_script, stream = Script.parse(stream)
        return cls(amount, locking_script), stream

    def get_amount(self) -> int:
        return self.__amount

    def get_addr(self) -> str:
        return self.__addr

    def get_locking_script(self) -> Script:
        return self.__locking_script

    __tableName = "tx_outputs"
    __tableCol = ["tx_id", "indexTx", "locking_script"]

    def query(self):
        # TODO: Fill values
        values = [

        ]
        return "INSERT INTO {} () VALUES ()".format(self.__tableName, ", ".join(self.__tableCol), ", ".join(values))
