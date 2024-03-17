import time
from notification import notification

class MonitoringClient:
    def __init__(self, error_threshold=5, error_interval=300):
        self.error_count = 0
        self.last_error_time = None
        self.error_threshold = error_threshold
        self.error_interval = error_interval

    def record_success(self):
        self.error_count = 0
        self.last_error_time = None

    def record_error(self, error_message):
        current_time = time.time()

        if self.last_error_time is None or current_time - self.last_error_time >= self.error_interval:
            self.error_count = 1
            self.last_error_time = current_time
        else:
            self.error_count += 1

        if self.error_count >= self.error_threshold:
            self.send_alert(error_message)
            self.error_count = 0

    def send_alert(self, error_message):
        subject = "Trading Bot Alert"
        message = f"An error occurred in the trading bot:\n\n{error_message}"
        notification(subject, message)
