import struct
import hashlib

NETWORK_MAGIC = b'\xf9\xbe\xb4\xd9'

class NetworkEnvelope:
    def __init__(self, command, payload):
        self.command = command
        self.payload = payload

    def serialize(self):
        return NETWORK_MAGIC + self.command + b'\x00' * (12 - len(self.command)) + struct.pack('<I', len(self.payload)) + hashlib.sha256(hashlib.sha256(self.payload).digest()).digest()[:4] + self.payload

    @classmethod
    def parse(cls, data):
        if data[:4] != NETWORK_MAGIC:
            raise Exception('Invalid magic')
        command = data[4:16].split(b'\x00')[0]
        length = struct.unpack('<I', data[16:20])[0]
        checksum = data[20:24]
        payload = data[24:24+length]
        if checksum != hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]:
            raise Exception('Invalid checksum')
        return cls(command, payload)

    def __repr__(self):
        return f'NetworkEnvelop(command={self.command}, payload={self.payload})'