from .. import socketio


@socketio.on('connection', namespace='/test')
def confirmation_message(message):
    print(message)
    print(socketio)
