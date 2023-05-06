from flask_socketio import SocketIO, emit, send

socketio = SocketIO()


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit("message", "sa")


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on("message")
def handle_new_message(message):
    print(f"New message: {message}")
    emit("message", "sa")
