import os
import requests

def notification(message):
    """
    Sends a notification message either to a specified webhook URL fetched from
    an environment variable or prints it to stdout if no webhook URL is found.
    This function is designed for versatility, supporting messaging through webhooks
    (e.g., Slack) or simple stdout output for logging or testing.

    Parameters:
    - message (str): The notification message to send.

    Returns:
    None. The function outputs the message to a webhook or stdout, depending on
    the presence of the WEBHOOK_URL environment variable.
    """
    # Attempt to fetch the webhook URL from the environment variables
    webhook_url = os.getenv('WEBHOOK_URL')

    if webhook_url:
        print("Calling webhook with message:", message)
        # If WEBHOOK_URL is set, prepare and send the message as a JSON payload
        payload = {"text": message}
        response = requests.post(webhook_url, json=payload)
        # Check the response to determine if the POST was successful
        if response.status_code == 200:
            print("Notification sent successfully to webhook.")
        else:
            print(f"Failed to send notification to webhook. Status code: {response.status_code}, Response: {response.text}")
    else:
        # If no webhook URL is found, output the message to stdout
        print("Notification message (environment variable webhook URL provided):")
        print(message)

if __name__ == '__main__':
    notification("Testing notify")

