__package__ = "CarBufferDataStore"

import ErrorLog
import Utilities
import config
import json

class CarBufferDataStore():
    def __init__(self):
        super().__init__()
        self.error_log = ErrorLog.ErrorLog()
        self.utilities = Utilities.Utilities()
        self.outputBufferDir = config.OUTPUT_BUFFER_DIR
        self.bufferJsonFileName = config.BUFFER_JSON_FILE_NAME

    def insertData(self, data: dict) -> bool:
        try:
            with open(f"{self.outputBufferDir}/{self.bufferJsonFileName}", "a") as f:
                json.dump(data, f)
                f.write("\n")
            return True
        except Exception as e:
            self.error_log.saveErrorLog(time = self.utilities.getTimeStamp(), errorType = "Buffer", error = f"{e}")
            return False
    
    def readData(self) -> tuple[bool, list[dict]]:
        try:
            with open(f"{self.outputBufferDir}/{self.bufferJsonFileName}", "r") as f:
                data = json.load(f)
                return True, data
        except Exception as e:
            self.error_log.saveErrorLog(time = self.utilities.getTimeStamp(), errorType = "Buffer", error = f"{e}")
            return False, None
