import utils
from blockchain import Transaction


class TransactionMessage():
    command = b'transaction'
    __logger = utils.get_logger(__name__)

    def __init__(self, tx: Transaction):
        self.__tx = tx

    def get_tx(self) -> Transaction:
        return self.__tx

    def serialize(self):
        return self.__tx.serialize()

    @ classmethod
    def parse(cls, stream) -> tuple['TransactionMessage', bytes]:
        tx, stream = Transaction.parse(stream)
        return cls(tx), stream

    def __repr__(self):
        return f'TransactionMessage(tx={self.__tx})'

    @ classmethod
    def handler(cls, network, host, payload):
        peer = network.get_peer(host)
        if not (peer and peer.is_handshake_done()):
            cls.__logger.warning(
                f"Received tx message from {host} before handshake")
            return
        txmsg, _ = cls.parse(payload)
        tx = txmsg.get_tx()
        from blockchain import blockchain
        blockchain.receive_new_tx(tx, sender=host)
        network.remove_requested(tx.get_hash())
