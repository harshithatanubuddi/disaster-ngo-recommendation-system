# app/alerts/severity.py

SEVERITY_RULES = {
    "High": [
        "red warning",
        "extremely severe",
        "very heavy",
        "severe cyclonic"
    ],
    "Medium": [
        "orange warning",
        "heavy rainfall",
        "cyclonic storm"
    ],
    "Low": [
        "watch",
        "possible",
        "low pressure"
    ]
}

def estimate_severity(alert_text: str):
    """
    Estimate disaster severity using rule-based keyword matching.
    Returns (severity, confidence)
    """
    if not alert_text:
        return "Low", 0.0

    text = alert_text.lower()

    for severity, keywords in SEVERITY_RULES.items():
        for kw in keywords:
            if kw in text:
                return severity, 0.8

    return "Low", 0.4
