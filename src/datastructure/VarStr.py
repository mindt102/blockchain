from datastructure.VarInt import VarInt
from typing import Self


class VarStr:
    def __init__(self, string: str = ''):
        self.string = string
        self.length = VarInt(len(string))
        self.value = self.length.value + string.encode('utf-8')
        self.size = len(self.value)

    @classmethod
    def parse(cls, stream: bytes) -> Self:
        length, stream = VarInt.parse(stream)
        return cls(stream[:length.integer].decode('utf-8')), stream[length.integer:]

    def __repr__(self):
        return f'VarStr({self.string}, {self.value})'
