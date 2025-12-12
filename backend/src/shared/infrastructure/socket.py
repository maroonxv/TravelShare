from flask_socketio import SocketIO

# Initialize SocketIO
# Shared instance to be used across modules
socketio = SocketIO(cors_allowed_origins="*")
