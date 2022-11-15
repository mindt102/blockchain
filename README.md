# Quick Start

## 1. Install the docker and docker-compose

## 2. Build the docker image

```
docker compose build
```

## 3. Run the docker-compose

```
docker compose up
```

# Folder Structure

```
.
├── src
│   ├── network # network related classes
│   │   ├── __init__.py
│   │   ├── NetworkAddress.py # Represent a network address (services, ip, port)
│   │   ├── NetworkEnvelope.py # Represent a network message (command, payload)
│   │   ├── Peer.py # Represent a peer (host, port)
│   │   └── PeerConnection.py # Represent a socket connection to a peer (host, port, socket)
│   ├── protocols # protocol related classes
│   │   ├── __init__.py
│   │   ├── VersionMessage.py # Represent a version message
│   │   ├── VerackMessage.py # Represent a verack message
│   ├── utils # utility classes
│   │   ├── __init__.py
│   │   ├── get_logger.py # Return a logger instance with a given name
│   │   └── convert_ip.py # Convert an ip address from bytes to string and vice versa
│   └── Node.py # The main class of the node
├── main.py # The entry point of the node
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```
