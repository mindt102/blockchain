import hashlib

BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def hash256(s: bytes) -> bytes:
    '''Two rounds of sha256'''
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()


def hash160(s: bytes) -> bytes:
    '''sha256 followed by ripemd160'''
    return hashlib.new('ripemd160', hashlib.sha256(s).digest()).digest()


def encode_base58(s: bytes) -> str:
    # determine how many 0 bytes (b'\x00') s starts with
    count = 0
    for c in s:
        if c == 0:
            count += 1
        else:
            break
    # convert to big endian integer
    num = int.from_bytes(s, 'big')
    prefix = '1' * count
    result = ''
    while num > 0:
        num, mod = divmod(num, 58)
        result = BASE58_ALPHABET[mod] + result
    return prefix + result


def encode_base58check(s: bytes) -> str:
    '''Encode bytes to base58 with checksum'''
    return encode_base58(s + hash256(s)[:4])


def decode_base58(s: str) -> bytes:
    '''Decode base58 encoded string to bytes'''
    num = 0
    for char in s:
        num *= 58
        num += BASE58_ALPHABET.index(char)
    combined = num.to_bytes(32, 'big').lstrip(b'\x00')
    return combined


def decode_base58check(s: str) -> bytes:
    '''Decode base58 encoded string to bytes with checksum'''
    result = decode_base58(s)
    checksum = result[-4:]
    if hash256(result[:-4])[:4] != checksum:
        raise RuntimeError('bad address: {} {}'.format(
            checksum, hash256(result[:-4])[:4]))
    return result[:-4]
