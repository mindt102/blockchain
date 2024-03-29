
from datastructure import VarInt
from blockchain.opcode import *
import utils


class Script:
    __logger = utils.get_logger(__name__)

    def __init__(self, cmds: list[bytes] = []) -> None:
        self.cmds = cmds

    def __add__(self, other):
        return Script(self.cmds + other.cmds)

    @classmethod
    def get_lock(cls, addr: str) -> 'Script':
        """
        ScriptPubKey = OP_DUP + OP_HASH160 + PubKeyHash + OP_EQUALVERIFY + OP_CHECKSIG
        Stored in txout
        """
        return cls([b'\x76', b'\xa9', utils.decode_base58check(addr), b'\x88', b'\xac'])

    @ classmethod
    def get_unlock(cls, signature: bytes, pubkey: bytes) -> 'Script':
        """
        ScriptSig = Signature + PubKey
        Stored in txin
        """
        return cls([signature, pubkey])

    def evaluate(self, z) -> bool:
        cmds = self.cmds[:]
        stack = []
        alt_stack = []
        while cmds:
            cmd = cmds.pop(0)
            if len(cmd) == 1 and cmd > b'\x4d':
                op = OP_CODE_FUNCTIONS[cmd]
                if cmd in (0x63, 0x64):
                    if not op(stack, cmds):
                        self.__logger.warning("OP_IF/OP_NOTIF failed")
                        return False
                elif cmd in (0x6b, 0x6c):
                    if not op(stack, alt_stack, cmds):
                        self.__logger.warning(
                            "OP_TOALTSTACK/OP_FROMALTSTACK failed")
                        return False
                elif cmd in (0xac, 0xad, 0xae, 0xaf):
                    if not op(stack, z):
                        self.__logger.warning(
                            "OP_CHECKSIG/OP_CHECKSIGVERIFY/OP_CHECKMULTISIG/OP_CHECKMULTISIGVERIFY failed")
                        return False
                else:
                    if not op(stack):
                        self.__logger.warning(f"{op.__name__} failed")
                        return False
            else:
                stack.append(cmd)
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
    def parse(cls, stream: bytes) -> tuple['Script', bytes]:
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

    @classmethod
    def lock_to_addr(cls, script: 'Script') -> str:
        if (script.cmds[0] == b'\x76'
                and script.cmds[1] == b'\xa9'
                and script.cmds[3] == b'\x88'
                and script.cmds[4] == b'\xac'):
            return utils.encode_base58check(script.cmds[2])
        raise ValueError("Invalid lock script")

    def __repr__(self):
        return f'Script({self.to_json()})'

    def to_json(self) -> dict:
        return [cmd.hex() for cmd in self.cmds]
