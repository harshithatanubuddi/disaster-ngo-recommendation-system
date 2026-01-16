import csv
import os
from datetime import date

def save_snapshot(alerts):
    os.makedirs("data/alert_snapshots", exist_ok=True)
    filename = f"data/alert_snapshots/alerts_snapshot_{date.today()}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=alerts[0].keys())
        writer.writeheader()
        writer.writerows(alerts)

    return filename
