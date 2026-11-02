import os
import requests


def notification(message):
    """Post to the configured Mattermost incoming webhook, or log locally."""
    webhook_url = os.getenv("MATTERMOST_WEBHOOK_URL", "").strip()
    if not webhook_url:
        print("Notification message (Mattermost webhook not configured):")
        print(message)
        return

    try:
        response = requests.post(webhook_url, json={"text": message}, timeout=5)
        response.raise_for_status()
        print("Notification sent successfully to Mattermost.")
    except requests.RequestException:
        # Exception strings can include the secret webhook URL. Keep trade
        # handling alive and avoid logging credentials or response bodies.
        print("Mattermost notification failed; check the notification service.")


if __name__ == "__main__":
    notification("Testing notify")
