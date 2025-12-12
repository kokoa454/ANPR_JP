import config.config as config
import requests

class ErrorLog:
    @staticmethod
    def save_error_log(timestamp: str, error_type: str, error: str) -> None:
        ErrorLog._save_error_log_to_file(timestamp = timestamp, error_type = error_type, error = error)
        ErrorLog.save_error_log_to_db(timestamp = timestamp, error_type = error_type, error = error)

    @staticmethod
    def _save_error_log_to_file(timestamp: str, error_type: str, error: str) -> None:
        with open(f"{config.OUTPUT_LOGS_DIR}/{config.ERROR_LOG_FILE_NAME}", "a") as log_file:
            log_file.write(f"{timestamp} - {error_type} : {error}\n")

    @staticmethod
    def save_error_log_to_db(timestamp: str, error_type: str, error: str) -> None:
        try:
            headers = {config.API_NAME: config.API_KEY}
            response = requests.post(url = config.API_ERROR_DATA_URL, headers = headers, json = ErrorLog._format_data(timestamp = timestamp, error_type = error_type, error = error), timeout = config.DB_TIMEOUT_SEC)

            if not ErrorLog._check_request_status(response = response):
                ErrorLog._save_error_log_to_file(timestamp = timestamp, error_type = "DB", error = f"API connection check failed with status code. {response.status_code}")
        except Exception as e:
            ErrorLog._save_error_log_to_file(timestamp = timestamp, error_type = "DB", error = f"{e}")

    @staticmethod
    def _format_data(timestamp: str, error_type: str, error: str) -> dict:
        return {
            "timestamp": timestamp,
            "raspberry_pi_num": config.RASPBERRY_PI_NUM,
            "error_type": error_type,
            "error": error
        }

    @staticmethod
    def _check_request_status(response: requests.Response) -> bool:
        if response.status_code == 200:
            return True
        else:
            return False
