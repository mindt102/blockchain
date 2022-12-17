
from blockchain.Script import Script
# from blockchain.utils import getTxByHash
# from database.DatabaseController import DatabaseController
# from blockchain.TxOut import TxOut


class TxIn:
    def __init__(self, prev_tx: bytes, output_index: int, unlocking_script: Script = Script()) -> None:
        self.__prev_tx_hash = prev_tx
        self.__output_index = output_index
        self.__unlocking_script = unlocking_script

    def serialize(self) -> bytes:
        return self.__prev_tx_hash + self.__output_index.to_bytes(4, 'little') + self.__unlocking_script.serialize()

    def __repr__(self) -> str:
        return f'''TxIn(
    prev_tx={self.__prev_tx_hash},
    output_index={self.__output_index},
    unlocking_script={self.__unlocking_script}
)'''

    @classmethod
    def parse(cls, stream: bytes) -> tuple['TxIn', bytes]:
        prev_tx = stream[:32]
        stream = stream[32:]
        output_index = int.from_bytes(stream[:4], 'little')
        stream = stream[4:]
        unlocking_script, stream = Script.parse(stream)
        return cls(prev_tx, output_index, unlocking_script), stream

    def get_empty_copy(self) -> 'TxIn':
        return TxIn(self.__prev_tx_hash, self.__output_index, Script())

    def set_unlocking_script(self, unlocking_script: Script) -> None:
        self.__unlocking_script = unlocking_script

    def get_prev_tx_hash(self) -> bytes:
        return self.__prev_tx_hash

    def get_output_index(self) -> int:
        return self.__output_index

    def get_unlocking_script(self) -> Script:
        return self.__unlocking_script

    # __tableName = "tx_inputs"
    # __tableCol = ["tx_output_id", "unlocking_script"]

    # def insert(self):
    #     __db = DatabaseController()
    #     txId = getTxByHash(self.__prev_tx_hash)
    #     if not txId:
    #         print("Transaction not found")
    #     txOut = TxOut.select(txId, self.__output_index)
    #     if not txOut:
    #         print("Transaction output not found")
    #     values = (txOut, self.__unlocking_script.serialize())
    #     return __db.insert(self.__tableName, self.__tableCol, values)
