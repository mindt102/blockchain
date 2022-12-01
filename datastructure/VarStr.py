from datastructure.VarInt import VarInt


class VarStr:
    def __init__(self, string: str = ''):
        self.__value = string
        self.length = VarInt(len(string))
        # self.value = self.length.value + string.encode('utf-8')
        # self.size = len(self.value)

    @classmethod
    def parse(cls, stream: bytes) -> 'VarStr':
        length, stream = VarInt.parse(stream)
        return cls(stream[:length.get_value()].decode('utf-8')), stream[length.get_value():]

    def raw_serialize(self) -> bytes:
        return self.__value.encode('utf-8')

    def serialize(self) -> bytes:
        return self.length.serialize() + self.raw_serialize()

    def __repr__(self):
        return f'VarStr({self.__value})'

    def get_value(self) -> str:
        return self.__value
