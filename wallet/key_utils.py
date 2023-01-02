import os

from ellipticcurve.privateKey import PrivateKey
from ellipticcurve.publicKey import PublicKey

from utils.hashing import encode_base58check, hash160

from utils import config
__privkey_file = config["wallet"]["privatekey_path"]


def load_privatekey(privatekey_file):
    '''
    Initialize private key
    Create a new private key if one does not exist
    Else load the existing private key
    '''
    if os.path.exists(privatekey_file):
        with open(privatekey_file, "r") as f:
            privkey = PrivateKey.fromPem(f.read())
    else:
        privkey = PrivateKey()
        with open(privatekey_file, "w") as f:
            f.write(privkey.toPem())
    return privkey


def load_publickey(privatekey: PrivateKey):
    return privatekey.publicKey()


def load_address(publickey: PublicKey):
    pubkey = publickey.toCompressed().encode()
    pubkeyhash = hash160(pubkey)
    return encode_base58check(pubkeyhash)


privkey: PrivateKey = load_privatekey(__privkey_file)
pubkey: PublicKey = load_publickey(privkey)
address: str = load_address(pubkey)
