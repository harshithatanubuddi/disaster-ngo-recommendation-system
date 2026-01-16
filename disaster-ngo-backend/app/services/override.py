def apply_override(data):
    return {
        "status": "human_override_applied",
        "final_disaster_type": data.overridden_prediction,
        "final_severity": data.overridden_severity,
        "final_ngos": data.overridden_ngos,
        "reviewer": data.reviewer_name,
        "reason": data.reason
    }
