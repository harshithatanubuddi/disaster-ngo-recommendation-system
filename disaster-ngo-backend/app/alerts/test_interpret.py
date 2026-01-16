from interpret_alert import interpret_alert

if __name__ == "__main__":
    alert = "IMD issues red warning for extremely severe cyclonic storm over Andhra Pradesh coast"

    result = interpret_alert(alert)

    print(result)
