import sys
import os
import json

# Add project root to path for local import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lambda_deploy.lambda_function import lambda_handler

TEST_INPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'test_inputs')


def load_test_input(file_name):
    path = os.path.join(TEST_INPUT_DIR, file_name)
    with open(path, 'r') as f:
        return json.load(f)


def run_test(file_name):
    """Run a test case by loading the input JSON and invoking the Lambda handler."""
    print(f"\n=== Running test: {file_name} ===")
    try:
        event = load_test_input(file_name)
        response = lambda_handler(event, context={})
        print("Lambda response:")
        print(json.dumps(response, indent=2))

        # Parse the stringified JSON in 'body'
        body = json.loads(response.get("body", "{}"))

        if body.get("alert", False):
            print("🚨 Anomaly Detected:", body.get("note", "Anomaly detected"))
        elif body.get("error", False):
            print("❌ Error:", body.get("error", "Unknown error"))
        else:
            print("✅ Normal payload processed")

    except Exception as e:
        print("❌ Error during test:", str(e))


if __name__ == "__main__":
    # Test with a valid payload that should process normally
    # Test with high temperature anomaly
    # Test with high vibration anomaly
    # Test with multiple anomalies in one payload
    # Test with edge case payloads to check robustness
    # Test with malformed payloads to ensure error handling
    test_files = [
        "valid_payload.json",
        "high_temp.json",
        "high_vibration.json",
        "low_humidity.json",
        "high_humidity.json",
        "multi_anomaly.json",
        "edge_case_payload.json",
        "edge_humidity.json",
        "malformed_payload.json",
        "missing_input.json"
    ]
    print("\n=== Starting Lambda Handler Tests ===\n")
    # Run each test case
    for test_file in test_files:
        run_test(test_file)

    print("\n=== All tests completed ===\n")
