import random
import time
from datetime import datetime, timezone
import json


def generate_payload(device_id="rack-01"):
    """Generate a random payload for the sensor."""
    payload = {
        "device_id": device_id,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "temperature": round(random.uniform(65, 100), 2),
        "humidity": round(random.uniform(30, 80), 2),
        "vibration": round(random.uniform(0.0, 1.0), 2)
    }
    return payload


def main():
    """Main function to simulate sensor data generation and print values."""
    try:
        while True:
            payload = generate_payload()
            print(json.dumps(payload))  # Could be redirected to AWS MQTT later
            time.sleep(5)  # Simulate 5-second intervals
    except KeyboardInterrupt:
        print("\nSimulation stopped.")


if __name__ == "__main__":
    main()