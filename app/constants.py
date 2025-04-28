# --- app/constants.py ---
# This file stores static constants for the CTF Dashboard
# including event difficulty definitions, random filler lines, and config settings.

# --- Difficulty and Hints for Event Types ---
# Maps event types to visual color, difficulty label, points earned, and hint text
event_difficulty = {
    "Successful Login": {"color": "success", "difficulty": "Easy",   "points": 100, "hint": "Check recent login history for the user."},
    "Failed Login":     {"color": "fail",    "difficulty": "Medium", "points": 200, "hint": "Check for repeated login attempts or brute-force patterns."},
    "Account Lockout":  {"color": "lockout", "difficulty": "Hard",   "points": 300, "hint": "Check AD logs or lockout policy settings."},
    "Other":            {"color": "",        "difficulty": "Unknown","points":   0, "hint": "N/A"}
}

# --- Random filler lines ---
# These random lines are mixed with hints inside the challenge hint files to simulate real logs
random_lines = [
    "Analyzing endpoint behavior from host logs...",
    "Timestamp mismatch detected across authentication attempts.",
    "User agent suggests VPN access from external IP.",
    "Multiple failed login attempts detected in sequence.",
    "Successful login occurred after an IP geolocation shift.",
    "Audit trail shows permission changes made by user.",
    "Event correlation suggests lateral movement.",
    "Baseline behavior deviated at 03:14 AM.",
    "System registry key modified during session.",
    "Firewall policy adjusted without ticket documentation."
]

# --- Configurable maximum alerts setting ---
# How many alerts are generated when the CTF is first started
MAX_ALERTS_ON_START = 5
