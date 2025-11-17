__package__ = "ErrorLog"

import os

class ErrorLog:
    def __init__(self):
        os.makedirs("./logs", exist_ok=True)
        self.logFilePath = "./logs/error_log.txt"
    
    def saveErrorLog(self, message: str) -> None:
        with open(self.logFilePath, "a") as logFile:
            logFile.write(message + "\n")