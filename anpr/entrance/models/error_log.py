import config.config as config

class ErrorLog:
    @staticmethod
    def save_error_log(timestamp: str, error_type: str, error: str) -> None:
        with open(f"{config.OUTPUT_LOGS_DIR}/{config.ERROR_LOG_FILE_NAME}", "a") as log_file:
            log_file.write(f"{timestamp} - {error_type} : {error}\n")