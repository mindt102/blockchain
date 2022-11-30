from typing import Self


class VarInt:
    def __init__(self, integer: int):
        self.__value = integer

    def serialize(self) -> bytes:
        if self.__value < 0xfd:
            return bytes([self.__value])
        elif self.__value < 0xffff:
            return b'\xfd' + self.__value.to_bytes(2, 'little')
        elif self.__value < 0xffffffff:
            return b'\xfe' + self.__value.to_bytes(4, 'little')
        else:
            return b'\xff' + self.__value.to_bytes(8, 'little')

    @classmethod
    def parse(cls, stream: bytes) -> tuple[Self, bytes]:
        if stream[0] < 0xfd:
            return cls(stream[0]), stream[1:]
        elif stream[0] == 0xfd:
            return cls(int.from_bytes(stream[1:3], 'little')), stream[3:]
        elif stream[0] == 0xfe:
            return cls(int.from_bytes(stream[1:5], 'little')), stream[5:]
        else:
            return cls(int.from_bytes(stream[1:9], 'little')), stream[9:]

    def __repr__(self):
        return f'VarInt({self.__value})'

    def get_value(self) -> int:
        return self.__value
