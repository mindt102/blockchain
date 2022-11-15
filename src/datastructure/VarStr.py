from datastructure.VarInt import VarInt

class VarStr:
    def __init__(self, string: str=None):
        self.string = string
        self.length = VarInt(len(string))
        self.value = self.length.value + string.encode('utf-8')
        self.size = len(self.value)


    @classmethod
    def parse(cls, bytes: bytes) -> str:
        length = VarInt.parse(bytes)
        return cls(bytes[length.size:length.size+length.integer].decode('utf-8'))

    def __repr__(self):
        return f'VarStr({self.string}, {self.value})'