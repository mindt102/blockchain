class InvItem:
    MSG_TX = 1
    MSG_BLOCK = 2

    def __init__(self, type: int, hash: bytes) -> None:
        self.__type = type
        self.__hash = hash

    def serialize(self) -> bytes:
        return self.__type.to_bytes(4, byteorder='little') + self.__hash

    @classmethod
    def parse(cls, stream: bytes) -> tuple['InvItem', bytes]:
        itype = int.from_bytes(stream[:4], byteorder='little')
        ihash = stream[4:36]
        return cls(itype, ihash), stream[36:]

    def __repr__(self) -> str:
        return f"InvItem({self.__type}, {self.__hash.hex()})"

    def get_type(self) -> int:
        return self.__type

    def get_hash(self) -> bytes:
        return self.__hash
