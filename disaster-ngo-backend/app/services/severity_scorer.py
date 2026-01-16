SEVERITY_MAP = {
    "Super Cyclonic Storm": ("Extreme", 1.0),
    "Very Severe Cyclonic Storm": ("Very High", 0.9),
    "Severe Cyclonic Storm": ("High", 0.8),
    "Cyclonic Storm": ("Moderate", 0.6),

    "Deep Depression": ("Moderate", 0.5),
    "Land Depression": ("Low", 0.4),
    "Depression": ("Low", 0.3),

    "Flood": ("High", 0.8),
    "Heatwave": ("Moderate", 0.6),
    "Landslide": ("High", 0.8),
    "Earthquake": ("Extreme", 1.0)
}

def score_severity(disaster_type: str):
    return SEVERITY_MAP.get(
        disaster_type,
        ("Unknown", 0.0)
    )
