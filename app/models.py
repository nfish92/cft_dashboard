# --- app/models.py ---
# This file defines the database models (tables) used in the CTF Dashboard.
# Models are built using SQLAlchemy ORM.

from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from . import db

# --- Helper function ---
def generate_uuid():
    """Generate a random UUID string."""
    return str(uuid.uuid4())

# --- Alert Model ---
class Alert(db.Model):
    """Represents a live alert/challenge in the CTF dashboard."""
    __tablename__ = 'alerts'

    uuid = db.Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    event_id = db.Column(db.String(10), nullable=False)  # Event code like 4624, 4625
    user = db.Column(db.String(64), nullable=False)      # Username associated with the alert
    ip = db.Column(db.String(64), nullable=False)        # IP address associated with the alert
    location = db.Column(db.String(128), nullable=False) # Location or geolocation
    event_type = db.Column(db.String(32), nullable=False) # Human readable type ("Failed Login", etc.)
    time_created = db.Column(db.DateTime, default=datetime.utcnow) # Timestamp when created

    # --- Relationships ---
    flag = db.relationship('Flag', backref='alert', uselist=False, cascade='all, delete-orphan')
    submissions = db.relationship('Submission', backref='alert', cascade='all, delete-orphan')

    def __repr__(self):
        """For easy debugging: returns alert UUID and event type."""
        return f"<Alert {self.uuid} [{self.event_type}]>"

    @property
    def description(self):
        """Nicely formatted alert description shown on the dashboard."""
        return f"{self.event_type} alert for {self.user} from {self.ip}"

# --- Flag Model ---
class Flag(db.Model):
    """Represents the secret 'flag' answer tied to each alert."""
    __tablename__ = 'flags'

    uuid = db.Column(UUID(as_uuid=False), db.ForeignKey('alerts.uuid'), primary_key=True)
    value = db.Column(db.String(128), nullable=False) # Actual FLAG{value} string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        """For easy debugging: shows UUID and flag value."""
        return f"<Flag {self.uuid}={self.value}>"

# --- Submission Model ---
class Submission(db.Model):
    """Represents a user's attempt to submit a flag."""
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    alert_uuid = db.Column(UUID(as_uuid=False), db.ForeignKey('alerts.uuid'), nullable=False)
    submitted_value = db.Column(db.String(128), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    score = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)  # Whether this submission correctly solved the challenge

    def __repr__(self):
        """For easy debugging: shows submission ID, status (✓ or ✗), and score."""
        status = '✓' if self.completed else '✗'
        return f"<Submission {self.id} {status} score={self.score}>"
