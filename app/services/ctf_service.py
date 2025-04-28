# --- app/services/ctf_service.py ---
"""
Service layer for CTF logic: creating alerts, planting flags, and generating challenge file structures.
This keeps complex business logic out of the route handlers for cleaner code organization.
"""

import time
import random
import uuid
from pathlib import Path
import json
from .. import db
from ..models import Alert, Flag

# Import random filler lines and event difficulty settings
from app.constants import random_lines, event_difficulty

def generate_random_alert():
    """
    Create a new Alert record in the database,
    build the challenge files on disk,
    create a Flag record linked to the alert,
    and return the new alert's UUID.
    """

    # --- Step 1: Create a database entry for the new alert ---
    alert = Alert(
        event_id=random.choice(["4624", "4625", "4740"]),  # Random event code
        user=random.choice(["alice", "bob", "charlie", "diana", "eve"]),  # Random user
        ip=random.choice(["192.168.1.10", "10.0.0.12", "203.0.113.55", "172.16.5.22", "198.51.100.88"]),  # Random IP
        location=random.choice(["New York, USA", "London, UK", "Berlin, Germany", "Tokyo, Japan", "São Paulo, Brazil"]),
        event_type=None  # Set based on event_id below
    )

    # Assign human-readable event type based on event_id
    if alert.event_id == "4625":
        alert.event_type = "Failed Login"
    elif alert.event_id == "4624":
        alert.event_type = "Successful Login"
    elif alert.event_id == "4740":
        alert.event_type = "Account Lockout"
    else:
        alert.event_type = "Other"

    db.session.add(alert)
    db.session.commit()  # Commit to assign UUID

    # --- Step 2: Build challenge files on disk ---
    create_fake_flag_challenge(alert.__dict__, alert.uuid)

    # --- Step 3: Create a corresponding flag entry ---
    flag_value = f"FLAG{{{alert.user}_{alert.ip}}}"  # Create unique flag string
    flag = Flag(uuid=alert.uuid, value=flag_value)
    db.session.add(flag)
    db.session.commit()

    return alert.uuid  # Return UUID for further use (e.g., WebSocket notifications)

def create_fake_flag_challenge(alert_data, alert_uuid):
    """
    Build a fake filesystem structure for the challenge.
    Write hint files across multiple folders and embed the flag into a random file.

    - Preferably writes to ~/Desktop/CyberHunt/
    - If no Desktop, falls back to /generated_challenges/ inside the project directory
    """

    # --- Determine where to store the challenge folders ---
    desktop_dir = Path.home() / "Desktop"
    if desktop_dir.exists():
        base_dir = desktop_dir / "CyberHunt"  # Store challenges under CyberHunt/ folder
    else:
        base_dir = Path(__file__).resolve().parent.parent.parent / "generated_challenges"  # Fallback for server deployments

    base = base_dir / f"Alert_{alert_uuid}"
    base.mkdir(parents=True, exist_ok=True)  # Create directory (including parents if needed)

    # --- Prepare hint content ---
    hint = event_difficulty.get(alert_data['event_type'], event_difficulty['Other'])['hint']

    # Define folder and file names to simulate logs and system events
    folders = ["auth_logs", "system_events", "network_traffic", "incident_notes", "user_profiles"]
    files = ["log.txt", "report.txt", "entry.txt"]

    # --- Create folder structure and files ---
    for d in folders:
        p = base / d
        p.mkdir(exist_ok=True)
        for fname in files:
            with open(p / fname, "w") as f:
                lines = random.sample(random_lines, 3)  # Pick 3 random fake log lines
                lines.append(f"Hint: {hint}")  # Add real hint to each file
                random.shuffle(lines)
                f.write("\n".join(lines))

    # --- Randomly embed the flag into one of the generated files ---
    all_txt = list(base.rglob("*.txt"))
    chosen = random.choice(all_txt)  # Pick one .txt file randomly
    with open(chosen, "a") as f:
        f.write(f"\n\nFLAG{{{alert_data['user']}_{alert_data['ip']}}}\n")  # Append flag at the bottom

    # (Optional) Future: Write metadata like JSON summaries if needed
