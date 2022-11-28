import os
from Role import Role
from ellipticcurve.privateKey import PrivateKey
from utils import encode_base58check, hash160


class Wallet(Role):
    '''Provide wallet functionality'''

    def __init__(self):
        self.wallet = self
        self.__privkey_file = "privkey.pem"
        self.__init_privkey()
        self.__pubkey = self.__privkey.publicKey()
        self.__init_addr()
        super().__init__(wallet=self)

    def __init_privkey(self):
        '''
        Initialize private key
        Create a new private key if one does not exist
        Else load the existing private key
        '''
        if os.path.exists(self.__privkey_file):
            with open(self.__privkey_file, "r") as f:
                self.__privkey = PrivateKey.fromPem(f.read())
        else:
            self.__privkey = self.generate_privkey()
            with open(self.__privkey_file, "w") as f:
                f.write(self.__privkey.toPem())

    def __init_addr(self):
        '''
        Generate address from public key
        '''
        version = b'\x00'
        pubkey = self.__pubkey.toCompressed().encode()
        pubkeyhash = hash160(pubkey)
        self.__addr = encode_base58check(version + pubkeyhash)

    def get_privkey(self):
        return self.__privkey

    def get_pubkey(self):
        return self.__pubkey

    def get_addr(self):
        return self.__addr

    @classmethod
    def generate_privkey(cls):
        return PrivateKey()
