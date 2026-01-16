from interpret_alert import interpret_alert

if __name__ == "__main__":
    test_alerts = [
        "IMD issues red warning for extremely severe cyclonic storm over Andhra Pradesh coast",
        "Heavy rainfall expected, orange warning issued for Kerala",
        "Low pressure area likely to form over Bay of Bengal"
    ]

    for alert in test_alerts:
        print("ALERT:", alert)
        result = interpret_alert(alert)
        print(result)
        print("=" * 60)
