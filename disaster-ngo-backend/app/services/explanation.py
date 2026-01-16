def generate_explanation(
    alert_text: str,
    predicted_type: str,
    confidence: float,
    severity_level: str,
    regions: list
):
    return {
        "model_reasoning": [
            f"Text patterns strongly matched '{predicted_type}' alerts",
            f"Confidence score = {confidence}",
            f"Severity inferred as '{severity_level}' based on IMD rules",
            f"Regions detected: {', '.join(regions) if regions else 'None'}"
        ],
        "limitations": [
            "Text-based inference only",
            "No real-time sensor or satellite input",
            "Human validation recommended for high-impact events"
        ]
    }
