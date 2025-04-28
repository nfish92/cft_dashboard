# --- app/routes/alerts.py ---
"""
Alerts Blueprint: Manage alert creation, listing, and re-triggering challenge folders.
Handles REST API endpoints for the CTF dashboard backend.
"""

from flask import Blueprint, request, jsonify, current_app, render_template
from .. import db, socketio
from ..models import Alert, Submission
from ..services.ctf_service import generate_random_alert, create_fake_flag_challenge
from app.constants import MAX_ALERTS_ON_START

# Create a Blueprint instance for alert-related APIs
bp = Blueprint('alerts', __name__, url_prefix='/alerts')

@bp.route('/list', methods=['GET'])
def list_alerts():
    """
    GET /alerts/list
    Return a JSON list of all alerts stored in the database.
    """
    alerts = Alert.query.all()
    alert_list = []
    for a in alerts:
        alert_list.append({
            'uuid': a.uuid,
            'event_id': a.event_id,
            'user': a.user,
            'ip': a.ip,
            'location': a.location,
            'event_type': a.event_type,
            'time_created': a.time_created.isoformat()  # <-- fixed (removed extra parentheses)
        })
    return jsonify(alert_list), 200

@bp.route('/create', methods=['POST'])
def create_alert():
    """
    POST /alerts/create
    Create a new random alert and its associated files, 
    only if fewer than MAX_ALERTS_ON_START active alerts exist.
    """
    # Count how many active alerts exist (no completed submissions linked)
    active_alerts_count = Alert.query.outerjoin(Submission) \
                          .filter((Submission.completed == False) | (Submission.id == None)) \
                          .count()

    if active_alerts_count >= MAX_ALERTS_ON_START:
        # Already too many active challenges
        return jsonify({'message': 'Maximum number of active alerts reached.'}), 400

    # Create a new random alert and push it to users via Socket.IO
    new_uuid = generate_random_alert()
    socketio.emit('new_alert', {'uuid': new_uuid})
    return jsonify({'uuid': new_uuid}), 201

@bp.route('/<string:alert_uuid>/trigger', methods=['POST'])
def trigger_alert(alert_uuid):
    """
    POST /alerts/<uuid>/trigger
    Rebuild the challenge folder/files for a specific existing alert.
    Useful if hint files were deleted and need to be recreated without changing DB.
    """
    alert = Alert.query.get_or_404(alert_uuid)  # Safely lookup alert or 404 if not found

    alert_data = {
        'uuid': alert.uuid,
        'event_type': alert.event_type,
        'user': alert.user,
        'ip': alert.ip,
        'time': alert.time_created.isoformat()
    }

    create_fake_flag_challenge(alert_data, alert_uuid)  # Recreate challenge files
    current_app.logger.info(f"Re-triggered CTF folder for alert {alert_uuid}")

    return ('', 204)  # Respond with 204 No Content
