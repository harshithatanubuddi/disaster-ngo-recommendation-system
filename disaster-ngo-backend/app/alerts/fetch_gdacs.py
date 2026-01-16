import requests
import feedparser
import logging
from datetime import datetime

from app.alerts.regions import extract_region
from app.alerts.severity import estimate_severity
from app.alerts.review import human_review_required

GDACS_FEED_URL = "https://www.gdacs.org/xml/rss.xml"


def fetch_gdacs_alerts():
    try:
        response = requests.get(GDACS_FEED_URL, timeout=5)
        response.raise_for_status()
    except Exception as e:
        logging.warning(f"GDACS fetch failed: {e}")
        return []   # 🔥 FAIL-SAFE: never crash backend

    feed = feedparser.parse(response.text)
    alerts = []

    for entry in feed.entries:
        title = entry.get("title", "")
        summary = entry.get("summary", "")
        alert_text = f"{title} {summary}".strip()

        # -------------------------------
        # REGION EXTRACTION
        # -------------------------------
        region, region_conf = extract_region(alert_text)

        # -------------------------------
        # SEVERITY ESTIMATION
        # -------------------------------
        severity, severity_conf = estimate_severity(alert_text)

        # -------------------------------
        # EVENT TYPE CONFIDENCE
        # -------------------------------
        type_conf = 0.9 if entry.get("gdacs_eventtype") else 0.5

        # -------------------------------
        # HUMAN REVIEW FLAG
        # -------------------------------
        needs_review = human_review_required(
            type_conf=type_conf,
            region_conf=region_conf,
            severity_conf=severity_conf
        )

        alerts.append({
            "alert_id": entry.get("id"),
            "alert_text": alert_text,

            "region": region,
            "region_confidence": region_conf,

            "severity": severity,
            "severity_confidence": severity_conf,

            "event_type": entry.get("gdacs_eventtype", "unknown"),
            "type_confidence": type_conf,

            "human_review_required": needs_review,

            "countries": entry.get("gdacs_country", "unknown"),
            "gdacs_alert_level": entry.get("gdacs_alertlevel", "unknown"),

            "source": "GDACS",
            "fetched_at": datetime.utcnow().isoformat()
        })

    return alerts
