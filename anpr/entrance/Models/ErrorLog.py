import config.config as config

class ErrorLog:
    @staticmethod
    def saveErrorLog(time: str, errorType: str, error: str) -> None:
        with open(config.OUTPUT_LOGS_DIR + "/error_log.txt", "a") as logFile:
            logFile.write(f"{time} - {errorType} : {error}\n")