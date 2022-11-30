from typing import Self
from datastructure import VarInt


class Script:
    def __init__(self, cmds: list[bytes] = []) -> None:
        self.cmds = cmds

    def __add__(self, other):
        return Script(self.cmds + other.cmds)

    @classmethod
    def get_lock(cls, addr: str) -> Self:
        return cls([b'\x76', b'\xa9', addr.encode(), b'\x88', b'\xac'])

    @ classmethod
    def get_unlock(cls, privkey: bytes) -> Self:
        # TODO: Implement
        return cls([privkey])

    def validate(self) -> bool:
        # TODO: Validate a script
        return True

    def raw_serialize(self) -> bytes:
        result = b''
        for cmd in self.cmds:
            length = len(cmd)
            if length < 0x4c:
                result += length.to_bytes(1, 'little')
            elif length < 0xff:
                result += b'\x4c' + length.to_bytes(1, 'little')
            elif length < 0xffff:
                result += b'\x4d' + length.to_bytes(2, 'little')
            else:
                result += b'\x4e' + length.to_bytes(4, 'little')
            result += cmd
        return result

    def serialize(self) -> bytes:
        return VarInt(len(self.cmds)).serialize() + self.raw_serialize()

    @classmethod
    def parse(cls, stream: bytes) -> tuple[Self, bytes]:
        length, stream = VarInt.parse(stream)
        cmds = []
        count = 0
        while count < length.get_value():
            cmd_length = int.from_bytes(stream[:1], 'little')
            stream = stream[1:]
            if cmd_length < 0x4c:
                pass
            elif cmd_length == 0x4c:
                cmd_length = int.from_bytes(stream[:1], 'little')
                stream = stream[1:]
            elif cmd_length == 0x4d:
                cmd_length = int.from_bytes(stream[:2], 'little')
                stream = stream[2:]
            else:
                cmd_length = int.from_bytes(stream[:4], 'little')
                stream = stream[4:]
            cmds.append(stream[:cmd_length])
            stream = stream[cmd_length:]
            count += 1
        return cls(cmds), stream

    def __repr__(self):
        return f'Script({self.cmds})'
