
from blockchain.Script import Script


class TxIn:
    def __init__(self, prev_tx: bytes, output_index: int, unlocking_script: Script = Script()) -> None:
        self.__prev_hash = prev_tx
        self.__output_index = output_index
        self.__unlocking_script = unlocking_script

    def serialize(self) -> bytes:
        return self.__prev_hash + self.__output_index.to_bytes(4, 'little') + self.__unlocking_script.serialize()

    def __repr__(self) -> str:
        return f'''TxIn(
    prev_tx={self.__prev_hash},
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
        return TxIn(self.__prev_hash, self.__output_index, Script())

    def set_unlocking_script(self, unlocking_script: Script) -> None:
        self.__unlocking_script = unlocking_script

    def get_prev_hash(self) -> bytes:
        return self.__prev_hash

    def get_output_index(self) -> int:
        return self.__output_index

    def get_unlocking_script(self) -> Script:
        return self.__unlocking_script
