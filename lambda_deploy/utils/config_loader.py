import os
import json
from dotenv import load_dotenv

CONFIG_PATH = "config.json"


def load_env():
    """Load environment variables from .env file."""
    load_dotenv()
    return {
        "endpoint": os.getenv("AWS_IOT_ENDPOINT"),
        "cert": os.getenv("CERT_PATH"),
        "key": os.getenv("KEY_PATH"),
        "ca": os.getenv("CA_PATH"),
    }


def load_config():
    """Load runtime configuration from config.json."""
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise RuntimeError(f"Missing config file: {CONFIG_PATH}")
    

# def test_env_loader():
#     """Prints .env config values for testing purposes."""
#     env = load_env()
#     print("[ENV TEST] Loaded AWS IoT config:", env)