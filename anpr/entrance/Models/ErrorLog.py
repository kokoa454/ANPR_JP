import os
import config.config as config
from Models.Utilities import Utilities

class ErrorLog:
    def __init__(self):
        self.utilities = Utilities()
        self.outputLogsDir = config.OUTPUT_LOGS_DIR
        self.logFilePath = f"{self.outputLogsDir}/error_log.txt"
        os.makedirs(self.outputLogsDir, exist_ok = True)

    def saveErrorLog(self, time: str, errorType: str, error: str) -> None:
        with open(self.logFilePath, "a") as logFile:
            logFile.write(f"{time} - {errorType} : {error}\n")