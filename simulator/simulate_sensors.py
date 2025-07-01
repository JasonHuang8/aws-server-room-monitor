import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import random
import time
from datetime import datetime, timezone
import json
import argparse
import ssl
import paho.mqtt.client as mqtt
from utils.config_loader import load_env, load_config


def generate_payload(device_id="rack-01"):
    """Generate a random payload for the sensor."""
    payload = {
        "device_id": device_id,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z").replace(":", "-"),
        "temperature": round(random.uniform(65, 100), 2),
        "humidity": round(random.uniform(30, 80), 2),
        "vibration": round(random.uniform(0.0, 1.0), 2)
    }
    return payload


def create_mqtt_client(env_vars):
    """Set up and return an MQTT client connected to AWS IoT."""
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.tls_set(
        ca_certs=env_vars["ca"],
        certfile=env_vars["cert"],
        keyfile=env_vars["key"],
        tls_version=ssl.PROTOCOL_TLSv1_2
    )
    client.connect(env_vars["endpoint"], port=8883)
    client.loop_start()
    return client


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
        env_vars = load_env()
        mqtt_client = create_mqtt_client(env_vars)
        topic = f"sensors/server-room/{args.device_id}"

        while True:
            payload = generate_payload(device_id=args.device_id)
            payload_json = json.dumps(payload)
            result = mqtt_client.publish(topic, payload_json)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                print(f"Failed to publish message: {result.rc}")
            print(f"Published to {topic}: {payload_json}")
            time.sleep(random.randint(args.min_interval, args.max_interval))  # Simulate intervals based on user input

    except KeyboardInterrupt:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("\nSimulation stopped.")


if __name__ == "__main__":
    main()