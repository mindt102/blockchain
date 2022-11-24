from typing import Self


class VarInt:
    def __init__(self, integer: int):
        self.integer = integer

        if integer < 0xfd:
            self.value = bytes([integer])
        elif integer < 0xffff:
            self.value = b'\xfd' + integer.to_bytes(2, 'little')
        elif integer < 0xffffffff:
            self.value = b'\xfe' + integer.to_bytes(4, 'little')
        else:
            self.value = b'\xff' + integer.to_bytes(8, 'little')
        self.size = len(self.value)

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
        return f'VarInt({self.integer}, {self.value})'
