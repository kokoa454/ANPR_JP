__package__ = "ErrorLog"

import os
import config
from Utilities import Utilities

class ErrorLog:
    def __init__(self):
        self.utilities = Utilities()
        os.makedirs(config.OUTPUT_LOGS_DIR, exist_ok=True)
        self.logFilePath = f"{config.OUTPUT_LOGS_DIR}/error_log.txt"
    
    def saveErrorLog(self, message: str) -> None:
        with open(self.logFilePath, "a") as logFile:
            logFile.write(f"{self.utilities.getTimeStamp()} - {message}\n")