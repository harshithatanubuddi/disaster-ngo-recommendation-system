# app/services/process_alerts.py

from app.alerts.fetch_gdacs import fetch_gdacs_alerts
from app.alerts.interpret_alert import interpret_alert
from app.alerts.snapshot import save_snapshot
from app.alerts.india_filter import is_india_relevant

# 🔹 Alias to avoid name collisions
from app.services.recommendation_engine import recommend_ngos as recommend_ngos_engine

def process_live_alerts(db):
    # 1️⃣ Fetch global alerts
    alerts = fetch_gdacs_alerts()

    if not alerts:
        return {
            "mode": "live",
            "status": "no_alerts",
            "message": "No live alerts available at this time.",
            "results": []
        }

    # 2️⃣ India relevance filter (POST-ingestion)
    india_alerts = [a for a in alerts if is_india_relevant(a)]

    if not india_alerts:
        return {
            "mode": "live",
            "status": "no_india_alerts",
            "message": "No India-related live alerts available at this time."
        }

    # 3️⃣ Snapshot ONLY India-relevant alerts (reproducibility)
    save_snapshot(india_alerts)

    results = []

    # 4️⃣ Interpret + recommend
    for alert in india_alerts:
        interpretation = interpret_alert(alert["alert_text"])

        # 🚨 Safety gate
        if interpretation["human_review_required"]:
            ngos = []
        else:
            ngos = recommend_ngos_engine(
                db=db,
                region=interpretation["region"],
                disaster_type=interpretation["disaster_type"],
                severity=interpretation["severity"]
            )

        results.append({
            "alert_text": alert["alert_text"],
            "interpretation": interpretation,
            "recommended_ngos": ngos
        })

    return {
        "mode": "live",
        "status": "success",
        "results": results
    }
