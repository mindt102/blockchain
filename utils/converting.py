def ip_string_to_bytes(ip: str) -> bytes:
    return b'\x00'*10 + b'\xFF'*2 + bytes(map(int, ip.split('.')))


def ip_bytes_to_string(ip: bytes) -> str:
    return '.'.join(map(str, ip[-4:]))


def bits_to_target(bits: int) -> int:
    exponent = bits >> 24
    coefficient = bits & 0xFFFFFF
    return coefficient * 256**(exponent - 3)


def target_to_bits(target: int) -> int:
    exponent = 0
    while target > 0xFFFFFF:
        target >>= 8
        exponent += 1
    return (exponent + 3 << 24) | target
