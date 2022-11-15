class VerAckMessage:
    """
    This class re
    """

    command = b"verack"

    def __init__(self):
        pass

    def serialize(self):
        return b""

    @classmethod
    def parse(cls, data):
        return cls()

    @classmethod
    def handle(cls, node, host, payload):
        node.peers[host].received_verack()

    def __repr__(self):
        return f"VerAckMessage()"