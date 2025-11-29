import os
import config.config as config
from Models.Utilities import Utilities

class ErrorLog:
    def __init__(self):
        self.utilities = Utilities()
        self.logFilePath = f"../{config.OUTPUT_LOGS_DIR}/error_log.txt"
        os.makedirs(self.logFilePath, exist_ok = True)

    def saveErrorLog(self, time: str, errorType: str, error: str) -> None:
        with open(self.logFilePath, "a") as logFile:
            logFile.write(f"{time} - {errorType} : {error}\n")