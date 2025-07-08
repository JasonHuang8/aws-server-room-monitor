import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.config_loader import load_env, load_config

def test_load_env():
    """Test loading environment variables from .env file."""
    env = load_env()
    print("Loaded .env variables:")
    for key, value in env.items():
        print(f"{key}: {value}")


def test_load_config():
    """Test loading the configuration from config.json."""
    config = load_config()
    print("\nLoaded config.json:")
    for key, value in config.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    test_load_env()
    test_load_config()
