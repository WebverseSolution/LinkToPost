import json
import os

CRED_FILE = "credentials.json"

def load_credentials():
    """
    Load credentials from a local JSON file.
    Returns an empty dictionary if the file doesn't exist or is unreadable.
    """
    if not os.path.exists(CRED_FILE):
        return {}

    try:
        with open(CRED_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}
    except Exception:
        return {}


def save_credentials(data):
    """
    Save credentials dictionary to a local JSON file.
    Returns True if successful, False otherwise.
    """
    try:
        with open(CRED_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False
