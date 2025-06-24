import random
import time
from datetime import datetime, timezone
import json
import argparse


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


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Sensor Simulator for Server Room Monitoring")
    parser.add_argument("--device-id", type=str, default="rack-01", help="Device ID")
    parser.add_argument("--min-interval", type=int, default=5, help="Minimum send interval (seconds)")
    parser.add_argument("--max-interval", type=int, default=10, help="Maximum send interval (seconds)")
    return parser.parse_args()


def main():
    """Main function to simulate sensor data generation and print values."""
    try:
        args = parse_args()
        while True:
            payload = generate_payload(device_id=args.device_id)
            print(json.dumps(payload))  # Could be redirected to AWS MQTT later
            time.sleep(random.randint(args.min_interval, args.max_interval))  # Simulate 5-second intervals
    except KeyboardInterrupt:
        print("\nSimulation stopped.")


if __name__ == "__main__":
    main()