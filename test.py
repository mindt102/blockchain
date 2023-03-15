import socketio

sio = socketio.Client()


# @sio.event
# def connect():


@sio.event
def message(data):
    print(f"Received message: {data}")
    print()

@sio.event
def mempool(data):
    print(f"Received mempool: {data}")
    print()

@sio.event
def block(data):
    print(f"Received block: {data}")
    print()

sio.connect('http://localhost:3000')
sio.wait()
