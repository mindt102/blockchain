import utils
import struct

class NetworkAddress:
    def __init__(self, services=1, ip="127.0.0.1", port=8333):
        self.services = services

        if isinstance(ip, str):
            self.ip = utils.ip_string_to_bytes(ip)
        else:
            self.ip = ip

        self.port = port

    def serialize(self):
        return struct.pack('<Q', self.services) + self.ip + struct.pack('>H', self.port)

    @classmethod
    def parse(cls, data):
        services = struct.unpack('<Q', data[:8])[0]
        ip = data[8:24]
        port = struct.unpack('>H', data[24:26])[0]
        return cls(services, ip, port)

    def get_ip_string(self):
        return utils.ip_bytes_to_string(self.ip)

    def __repr__(self):
        return f'NetworkAddress(services={self.services}, ip={self.get_ip_string()}, port={self.port})'
