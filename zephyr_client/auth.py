import os

def get_auth_headers():
    token = os.getenv('ZEPHYR_API_TOKEN')
    if not token:
        raise ValueError("ZEPHYR_API_TOKEN is not set in environment variables")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
