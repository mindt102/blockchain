import os

from ellipticcurve.ecdsa import Ecdsa
from ellipticcurve.privateKey import PrivateKey

from blockchain import Blockchain, Script, Transaction, TxIn, TxOut
from Role import Role
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
        pubkey = self.__pubkey.toCompressed().encode()
        pubkeyhash = hash160(pubkey)
        self.__addr = encode_base58check(pubkeyhash)

    def get_privkey(self):
        return self.__privkey

    def get_pubkey(self):
        return self.__pubkey

    def get_addr(self):
        return self.__addr

    def create_transaction(self, to_addr: str, amount: int):
        '''Create a transaction to send coins to another address'''
        # TODO: IMPLEMENT @Trang
        blockchain: Blockchain = self.get_blockchain()
        utxo_sets = blockchain.get_UTXO_set()
        selected_utxo = self.select_utxo(amount, utxo_sets)
        inputs: list[TxIn] = []
        total_input = 0
        for key, utxo in selected_utxo.items():
            prev_hash, index = key
            tx_in = TxIn(prev_hash, index)
            inputs.append(tx_in)
            total_input += utxo.get_amount()
        change = total_input - amount
        assert change >= 0
        change_output = TxOut(change, addr=self.get_addr())
        spending_output = TxOut(amount, addr=to_addr)
        outputs: list[TxOut] = [change_output, spending_output]

        tx = Transaction(inputs, outputs)
        self.sign_transaction(tx)
        return tx

    @classmethod
    def generate_privkey(cls):
        return PrivateKey()

    def sign_transaction(self, tx: Transaction):
        '''Sign a transaction'''
        signature = Ecdsa.sign(tx.get_signing_data(),
                               self.get_privkey()).toDer()
        pubkey = self.get_pubkey().toCompressed().encode()
        unlocking_script = Script.get_unlock(signature, pubkey)
        tx.set_unlocking_script(unlocking_script)

    def select_utxo(self, amount: int, utxo_set: dict[tuple[bytes, int], TxOut]) -> dict[tuple[bytes, int], TxOut]:
        '''Select UTXO to spend. utxo_set is a dict with key: (prev_hash, output_index) and value: TxOut'''
        # TODO: IMPLEMENT @Trang
        # ... ht is doing
        total = 0
        selected_utxo = dict()
        
        for key, value in utxo_set.items():
            coin = value.get_amount()
            selected_utxo[key] = value
            total += coin
            if total >= amount:
                return selected_utxo
        raise ValueError(f"Not enough coin. Current balance: {total}")