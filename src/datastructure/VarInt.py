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
    def parse(cls, bytes: bytes) -> int:
        if bytes[0] < 0xfd:
            return cls(bytes[0])
        elif bytes[0] == 0xfd:
            return cls(int.from_bytes(bytes[1:3], 'little'))
        elif bytes[0] == 0xfe:
            return cls(int.from_bytes(bytes[1:5], 'little'))
        else:
            return cls(int.from_bytes(bytes[1:9], 'little'))

    def __repr__(self):
        return f'VarInt({self.integer}, {self.value})'