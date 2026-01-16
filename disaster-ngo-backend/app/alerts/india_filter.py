# app/alerts/india_filter.py

INDIA_STATES = [
    "Andhra Pradesh",
    "Telangana",
    "Tamil Nadu",
    "Odisha",
    "West Bengal",
    "Kerala",
    "Karnataka",
    "Maharashtra",
    "Gujarat",
    "Goa",
    "Assam",
    "Bihar",
    "Jharkhand",
    "Chhattisgarh",
    "Uttar Pradesh",
    "Madhya Pradesh",
    "Rajasthan"
]


def is_india_relevant(alert):
    """
    Returns True if the alert is relevant to India.
    """

    text = alert.get("alert_text", "").lower()

    # 1️⃣ Explicit India mention
    if "india" in text:
        return True

    # 2️⃣ Indian state mention
    for state in INDIA_STATES:
        if state.lower() in text:
            return True

    # 3️⃣ GDACS country metadata
    countries = alert.get("countries", "")
    if "india" in countries.lower():
        return True

    return False
