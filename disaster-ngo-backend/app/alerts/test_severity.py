from severity import estimate_severity

if __name__ == "__main__":
    alert = "IMD issues red warning with extremely severe cyclonic storm"

    severity, confidence = estimate_severity(alert)

    print(severity)
    print(confidence)
