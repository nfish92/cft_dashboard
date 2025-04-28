# --- manage.py ---
# This is the main entry point for running your Flask app during development.
# It runs the app using Flask-SocketIO to support real-time WebSocket updates.

import eventlet
eventlet.monkey_patch()  # Patch standard library to make it non-blocking for WebSocket handling

from app import create_app, socketio  # Import app factory and the initialized SocketIO server

# Create the Flask app instance
app = create_app()

if __name__ == '__main__':
    # Only run the server if this script is executed directly (not imported)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
