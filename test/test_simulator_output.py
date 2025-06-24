import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
import json
from simulator.simulate_sensors import generate_payload


class TestSensorSimulator(unittest.TestCase):
    def test_generate_payload_keys_exist(self):
        payload = generate_payload()
        expected_keys = {"device_id", "timestamp", "temperature", "humidity", "vibration"}
        self.assertTrue(expected_keys.issubset(payload.keys()))

    def test_generate_payload_types(self):
        payload = generate_payload()
        self.assertIsInstance(payload["device_id"], str)
        self.assertIsInstance(payload["timestamp"], str)
        self.assertIsInstance(payload["temperature"], float)
        self.assertIsInstance(payload["humidity"], float)
        self.assertIsInstance(payload["vibration"], float)

    def test_generate_payload_ranges(self):
        payload = generate_payload()
        self.assertGreaterEqual(payload["temperature"], 65)
        self.assertLessEqual(payload["temperature"], 100)
        self.assertGreaterEqual(payload["humidity"], 30)
        self.assertLessEqual(payload["humidity"], 80)
        self.assertGreaterEqual(payload["vibration"], 0.0)
        self.assertLessEqual(payload["vibration"], 1.0)

    def test_payload_json_serializable(self):
        payload = generate_payload()
        try:
            json_str = json.dumps(payload)
            self.assertIsInstance(json_str, str)
        except TypeError:
            self.fail("Payload is not JSON serializable")


if __name__ == "__main__":
    unittest.main()