from network.NetworkAddress import NetworkAddress
from network.NetworkEnvelope import NetworkEnvelope
from network.Peer import Peer
from network.Network import Network
from utils import config, get_logger

__logger = get_logger(__name__)

network = Network(config=config["network"])
__logger.info("Network initialized.")
