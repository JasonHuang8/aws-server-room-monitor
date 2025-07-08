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
    print(f"\n=== Running test: {file_name} ===")
    try:
        event = load_test_input(file_name)
        response = lambda_handler(event, context={})
        print("Lambda response:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print("Error:", str(e))


if __name__ == "__main__":
    test_files = [
        "valid_payload.json",
        "edge_case_payload.json",
        "malformed_payload.json"
    ]
    for test_file in test_files:
        run_test(test_file)

    print("\n=== All tests completed ===\n")
