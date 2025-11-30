from Models.ErrorLog import ErrorLog
from Models.Utilities import Utilities
import config.config as config
import os
import json

class CarBufferDataStore():
    _instance = None

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def insertData(self, data: dict) -> bool:
        if os.path.exists(f"{config.OUTPUT_BUFFER_DIR}/{config.BUFFER_JSON_FILE_NAME}") == False:
            bufferData = []
        else:
            status, bufferData = self.readData()
            if status == False:
                return False
        bufferData.append(data)
        try:
            with open(f"{config.OUTPUT_BUFFER_DIR}/{config.BUFFER_JSON_FILE_NAME}", "w") as f:
                json.dump(bufferData, f, indent = 4)
            return True
        except Exception as e:
            ErrorLog.saveErrorLog(time = Utilities.getTimeStamp(), errorType = "Buffer", error = f"{e}")
            return False
    
    def readData(self) -> tuple[bool, list[dict]]:
        try:
            with open(f"{config.OUTPUT_BUFFER_DIR}/{config.BUFFER_JSON_FILE_NAME}", "r") as f:
                data = json.load(f)
                return True, data
        except Exception as e:
            ErrorLog.saveErrorLog(time = Utilities.getTimeStamp(), errorType = "Buffer", error = f"{e}")
            return False, None
