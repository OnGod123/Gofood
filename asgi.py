"""
ASGI entry point for running Flask-SocketIO app with eventlet or hypercorn.
"""
from app import create_app, socketio

app = create_app()
asgi_app = socketio.asgi_app(app)

