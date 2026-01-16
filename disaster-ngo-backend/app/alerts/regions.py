# app/alerts/regions.py

INDIA_STATES = [
    "Andhra Pradesh",
    "Telangana",
    "Tamil Nadu",
    "Odisha",
    "West Bengal",
    "Kerala",
    "Karnataka"
]

def extract_region(alert_text: str):
    """
    Extract region name from alert text using gazetteer matching.
    Returns (region, confidence)
    """
    if not alert_text:
        return "Unknown", 0.0

    text = alert_text.lower()

    for state in INDIA_STATES:
        if state.lower() in text:
            return state, 0.9  # high confidence (explicit mention)

    return "Unknown", 0.3  # low confidence fallback
