def classify_disaster(alert_text):
    """
    Returns: (disaster_type, confidence)
    Rule-based disaster classification using alert terminology.
    """

    text = alert_text.lower()

    DISASTER_RULES = {
        "Cyclone": [
            "cyclone", "cyclonic storm", "severe cyclonic",
            "very severe cyclonic", "tropical storm",
            "depression over", "low pressure area"
        ],
        "Flood": [
            "flood", "flooding", "inundation",
            "heavy rainfall", "very heavy rainfall",
            "cloudburst"
        ],
        "Heatwave": [
            "heatwave", "heat wave", "extreme heat",
            "high temperature"
        ],
        "Earthquake": [
            "earthquake", "seismic", "tremor"
        ]
    }

    for disaster, keywords in DISASTER_RULES.items():
        for kw in keywords:
            if kw in text:
                return disaster, 0.9

    return "Unknown", 0.5
