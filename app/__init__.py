# --- app/__init__.py ---
# Initializes and configures the main Flask application.
# - Loads configuration settings
# - Sets up extensions (DB, Migrations, SocketIO)
# - Registers modular blueprints

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO

# --- Instantiate extensions ---
db = SQLAlchemy()  # ORM: database interactions
migrate = Migrate()  # DB schema migrations
socketio = SocketIO(async_mode="eventlet")  # Real-time WebSocket support using eventlet

def create_app(config_class=None):
    """
    Application factory function.
    Creates and configures the Flask app instance.

    Args:
        config_class (optional): Pass custom config class; defaults to DevelopmentConfig.

    Returns:
        Flask app instance
    """
    app = Flask(__name__)

    # 1) Load configuration
    if config_class:
        app.config.from_object(config_class)  # For testing, production overrides
    else:
        from .config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)  # Default to local dev settings

    # 2) Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)

    # 3) Register blueprints (modular routes)
    from .routes.alerts import bp as alerts_bp
    from .routes.ctf import bp as ctf_bp
    app.register_blueprint(alerts_bp)
    app.register_blueprint(ctf_bp)

    return app
