# --- wsgi.py ---
# This file is used for production deployments (like Gunicorn, uWSGI, etc.)

from app import create_app, db  # Import app factory and database instance
from flask_migrate import Migrate  # Import migration tool to handle database migrations

# Create Flask app instance
app = create_app()

# Bind database migrations to the app and db
migrate = Migrate(app, db)
