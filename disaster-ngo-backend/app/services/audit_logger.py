import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_PATH = DATA_DIR / "audit_logs.json"


def log_event(event_type: str, payload: dict):
    # 1️⃣ Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 2️⃣ Load existing logs safely
    if LOG_PATH.exists():
        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []
    else:
        logs = []

    # 3️⃣ Append new log
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "payload": payload
    }

    logs.append(entry)

    # 4️⃣ Write back to file
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)
