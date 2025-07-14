import sys
import os
import signal
import threading
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import random
import time
from datetime import datetime, timezone
import json
import argparse
import ssl
import paho.mqtt.client as mqtt
from concurrent.futures import ThreadPoolExecutor
from utils.config_loader import load_env, load_config


def generate_payload(device_id="rack-01", anomaly_rate=0.05):
    """Generate a random payload for the sensor, optionally injecting anomalies."""
    inject_anomaly = random.random() < anomaly_rate
    # Use triangular skewing for realism
    temperature = round(random.triangular(65.0, 72.0, 95.0), 2)
    humidity = round(random.triangular(25.0, 45.0, 70.0), 2)
    vibration = round(random.triangular(0.0, 0.15, 1.0), 2)

    if inject_anomaly:
        anomaly_type = random.choice(["temp", "humidity", "vibration"])
        if anomaly_type == "temp":
            temperature = round(random.uniform(90.0, 100.0), 2)
        elif anomaly_type == "humidity":
            humidity = round(random.choice([random.uniform(10.0, 18.0), random.uniform(65.0, 75.0)]), 2)
        elif anomaly_type == "vibration":
            vibration = round(random.uniform(0.6, 1.0), 2)

    return {
        "device_id": device_id,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "temperature": temperature,
        "humidity": humidity,
        "vibration": vibration
    }


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
    parser = argparse.ArgumentParser(
        description="Sensor Simulator for Server Room Monitoring"
        )
    parser.add_argument("--num-racks", type=int,
                        default=1, help="Number of server racks to simulate")
    parser.add_argument("--device-id", type=str,
                        default="rack-01", help="Device ID")
    parser.add_argument("--min-interval", type=int,
                        default=5, help="Minimum send interval (seconds)")
    parser.add_argument("--max-interval", type=int,
                        default=10, help="Maximum send interval (seconds)")
    parser.add_argument("--num-messages", type=int,
                        help="Optional number of messages to send before stopping (per rack)")
    parser.add_argument("--anomaly-rate", type=float, default=0.05,
                        help="Probability [0–1] that a payload contains an anomaly")

    args = parser.parse_args()

    # Safeguard: Check if --device-id was explicitly set
    if args.num_racks > 1 and "--device-id" in sys.argv:
        parser.error("Cannot use --device-id when --num-racks > 1. Device IDs are auto-generated in multi-rack mode.")

    return args


def setup_signal_handlers(stop_event):
    def signal_handler(sig, frame):
        print("\n[Main] Shutdown signal received.")
        stop_event.set()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def simulate_rack(device_id, env_vars, min_interval,
                  max_interval, stop_event, anomaly_rate=0.05, num_messages=None):
    mqtt_client = create_mqtt_client(env_vars)
    topic = f"sensors/server-room/{device_id}"
    message_count = 0
    try:
        while not stop_event.is_set():
            reached_limit = (num_messages is not None and message_count >= num_messages)
            if reached_limit:
                break
            payload = generate_payload(device_id=device_id, anomaly_rate=anomaly_rate)
            payload_json = json.dumps(payload)
            result = mqtt_client.publish(topic, payload_json)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                print(f"[{device_id}] Failed to publish message: {result.rc}")
            print(f"[{device_id}] Published to {topic}: {payload_json}")
            message_count += 1
            time.sleep(random.randint(min_interval, max_interval))
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print(f"[{device_id}] Disconnected cleanly after sending {message_count} messages.")


def main():
    """Main function to simulate sensor data generation."""
    try:
        args = parse_args()
        env_vars = load_env()
        stop_event = threading.Event()
        setup_signal_handlers(stop_event)

        if args.num_racks == 1:
            simulate_rack(
                device_id=args.device_id,
                env_vars=env_vars,
                min_interval=args.min_interval,
                max_interval=args.max_interval,
                stop_event=stop_event,
                anomaly_rate=args.anomaly_rate,
                num_messages=args.num_messages
            )
        else:
            with ThreadPoolExecutor(max_workers=args.num_racks) as executor:
                for i in range(args.num_racks):
                    device_id = f"rack-{i+1:02d}"
                    executor.submit(
                        simulate_rack,
                        device_id,
                        env_vars,
                        args.min_interval,
                        args.max_interval,
                        stop_event,
                        args.anomaly_rate,
                        args.num_messages
                    )
    except KeyboardInterrupt:
        print("\nSimulation stopped.")


if __name__ == "__main__":
    main()
