# --- app/config.py ---
# Configuration classes for different environments (Development, Production)

import os

# `basedir` points to the directory where this file is located
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Base configuration shared by all environments.
    """
    # Secret key for session management, CSRF protection, etc.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-secure-production-secret-key'

    # Disable SQLAlchemy event system to improve performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """
    Development configuration.
    - Enables debug mode
    - Uses local SQLite database unless overridden
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DEV_DATABASE_URL') or
        'sqlite:///' + os.path.join(basedir, 'app.db')
    )

class ProductionConfig(Config):
    """
    Production configuration.
    - Disables debug mode
    - Pulls production database URL from environment, fallback to SQLite
    """
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or
        'sqlite:///' + os.path.join(basedir, 'app.db')
    )
