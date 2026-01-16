import requests
import config.config as config
from models.error_log import ErrorLog
from models.utilities import Utilities
from models.notification import Notification

class DBDatastore:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def insert_data(self, data: dict) -> bool:
        try:
            headers = {config.API_NAME: config.API_KEY}
            response = requests.post(url = config.API_NUMBER_PLATE_DATA_URL, headers=headers, json=data, timeout = config.DB_TIMEOUT_SEC)

            if self._check_request_status(response = response):
                return True
            else:
                return False
        except requests.RequestException as e:
            timestamp = Utilities.get_timestamp()
            ErrorLog.save_error_log(timestamp = timestamp, error_type = "DB", error = f"{e}")
            Notification.send_error_notification(timestamp = timestamp, error_type = "DB", error = f"{e}")
            return False

    def insert_buffer_data(self, data: list[dict]) -> bool:
        try:
            if self.insert_data(data = data) == True:
                return True
            else:
                return False
        except Exception as e:
            timestamp = Utilities.get_timestamp()
            ErrorLog.save_error_log(timestamp = timestamp, error_type = "DB", error = f"{e}")
            Notification.send_error_notification(timestamp = timestamp, error_type = "DB", error = f"{e}")
            return False

    def _check_request_status(self, response: requests.Response) -> bool:
        if response.status_code == 201:
            return True
        else:
            timestamp = Utilities.get_timestamp()
            ErrorLog.save_error_log(timestamp = timestamp, error_type = "DB", error = f"API connection check failed with status code. {response.status_code}")
            Notification.send_error_notification(timestamp = timestamp, error_type = "DB", error = f"API connection check failed with status code. {response.status_code}")
            return False
