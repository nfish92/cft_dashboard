# --- app/routes/ctf.py ---
"""
CTF Blueprint: Manage user-facing dashboard, flag submission flow, and starting the CTF challenges.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from ..models import Alert, Submission, Flag
from .. import db, socketio
from ..services.ctf_service import generate_random_alert
from app.constants import MAX_ALERTS_ON_START
from datetime import datetime
import uuid

# Create a Blueprint for the main CTF challenge site
bp = Blueprint('ctf', __name__)

@bp.route('/')
def dashboard():
    """
    GET /
    Main dashboard route.
    Displays all current active alerts.
    """
    alerts = Alert.query.outerjoin(Submission) \
        .filter((Submission.completed == False) | (Submission.id == None)).all()
    return render_template('dashboard.html', alerts=alerts)

@bp.route('/submit_flag', methods=['POST'])
def submit_flag():
    """
    POST /submit_flag
    Handle a user's flag submission (either via form or AJAX request).
    """
    # --- Extract user input ---
    if request.is_json:
        data = request.get_json()
        alert_uuid = data.get('uuid')
        user_flag = data.get('flag', '').strip()
    else:
        alert_uuid = request.form.get('uuid')
        user_flag = request.form.get('flag', '').strip()

    # --- Lookup correct flag ---
    alert = Alert.query.get_or_404(alert_uuid)
    correct_flag = alert.flag.value

    # --- Calculate score penalty based on elapsed time ---
    elapsed_secs = 0
    if getattr(alert.flag, 'created_at', None):
        elapsed_secs = (datetime.utcnow() - alert.flag.created_at).total_seconds()

    base = current_app.config.get('POINTS_BASE', 1000)
    rate = current_app.config.get('PENALTY_RATE', 1)
    penalty = min(int(elapsed_secs * rate), base)
    score = max(base - penalty, 0)

    # --- Record submission result ---
    completed = (user_flag == correct_flag)
    sub = Submission(alert_uuid=alert_uuid, submitted_value=user_flag, score=score, completed=completed)
    db.session.add(sub)
    db.session.commit()

    # --- If correct, maybe spawn a new alert if active count is below limit ---
    if completed:
        active = Alert.query.filter(
            ~Alert.submissions.any(Submission.completed == True)
        ).count()
        if active < current_app.config.get('MAX_ALERTS', 5):
            new_uuid = generate_random_alert()
            socketio.emit('new_alert', {'uuid': new_uuid})

    # --- Prepare response ---
    message = f"✅ Correct! You scored {score} points." if completed else '❌ Incorrect flag, try again.'
    success = completed

    # --- Return response depending on submission type ---
    if request.is_json:
        return jsonify({'message': message, 'success': success, 'score': score})

    if completed:
        flash(message, 'success')
        return redirect(url_for('ctf.flag_complete', uuid=alert_uuid))
    else:
        flash(message, 'danger')
        return redirect(url_for('ctf.dashboard'))

@bp.route('/flag_complete/<string:uuid>')
def flag_complete(uuid):
    """
    GET /flag_complete/<uuid>
    Displays a success page after solving an alert correctly.
    """
    submission = Submission.query.filter_by(alert_uuid=uuid, completed=True).order_by(Submission.timestamp.desc()).first()
    if not submission:
        flash('No completed submission found.', 'danger')
        return redirect(url_for('ctf.dashboard'))
    return render_template('flag_complete.html', submission=submission)

@bp.route('/start_ctf', methods=['POST'])
def start_ctf():
    """
    POST /start_ctf
    Start a new CTF session by generating MAX_ALERTS_ON_START alerts/challenges.
    """
    # --- Check current active alert count ---
    active_count = Alert.query.outerjoin(Submission) \
                   .filter((Submission.completed == False) | (Submission.id == None)) \
                   .count()

    if active_count >= MAX_ALERTS_ON_START:
        # Already enough active alerts, just reload dashboard
        return redirect(url_for('ctf.dashboard'))
    
    # --- Create new alerts up to MAX_ALERTS_ON_START ---
    to_create = MAX_ALERTS_ON_START - active_count
    for _ in range(to_create):
        generate_random_alert()

    # --- Reload dashboard with new challenges ---
    return redirect(url_for('ctf.dashboard'))

@bp.route('/reset_ctf', methods=['POST'])
def reset_ctf():
    """
    Resets the CTF round:
    - Deletes all current Alerts, Flags, Submissions
    - Generates a fresh batch of new alerts
    """
    # Delete all existing challenges
    Submission.query.delete()
    Flag.query.delete()
    Alert.query.delete()
    db.session.commit()

    # Generate new alerts
    for _ in range(MAX_ALERTS_ON_START):
        generate_random_alert()

    return redirect(url_for('ctf.dashboard'))
