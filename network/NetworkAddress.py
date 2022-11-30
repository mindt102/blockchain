import utils
import struct


class NetworkAddress:
    def __init__(self, ip="127.0.0.1", port=8333):

        if isinstance(ip, str):
            self.__ip = utils.ip_string_to_bytes(ip)
        else:
            self.__ip = ip

        self.__port = port

    def serialize(self):
        return self.__ip + self.__port.to_bytes(2, 'big')

    @classmethod
    def parse(cls, stream) -> tuple['NetworkAddress', bytes]:
        # services = struct.unpack('<Q', stream[:8])[0]
        ip = stream[:16]
        stream = stream[16:]
        port = int.from_bytes(stream[:2], 'big')
        stream = stream[2:]
        return cls(ip, port), stream

    def get_ip_string(self):
        return utils.ip_bytes_to_string(self.__ip)

    def __repr__(self):
        return f'NetworkAddress(ip={self.get_ip_string()}, port={self.__port})'

    def get_host(self):
        return self.get_ip_string()

    def get_port(self):
        return self.__port
