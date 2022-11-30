from protocols.AddrMessage import AddrMessage
from protocols.BlockMessage import BlockMessage
from protocols.GetDataMessage import GetDataMessage
from protocols.InvItem import InvItem
from protocols.InvMessage import InvMessage
from protocols.VerAckMessage import VerAckMessage
from protocols.VersionMessage import VersionMessage

messages = [VersionMessage, VerAckMessage,
            InvMessage, GetDataMessage, BlockMessage, AddrMessage]
