__package__ = "CarBufferDataStore"

import AbstractCarDataStore
import requests
import ErrorLog
import Utilities
import config
import json

class CarBufferDataStore(AbstractCarDataStore.AbstractCarDataStore):
    def __init__(self):
        super().__init__()
        self.error_log = ErrorLog.ErrorLog()
        self.utilities = Utilities.Utilities()
        self.outputBufferDir = config.OUTPUT_BUFFER_DIR
        self.bufferJsonFileName = config.BUFFER_JSON_FILE_NAME

    def insertData(self, timeStamp: str, data: dict) -> bool:
        try:
            with open(f"{self.outputBufferDir}/{self.bufferJsonFileName}", "a") as f:
                json.dump(data, f)
                f.write("\n")
            return True
        except Exception as e:
            self.error_log.saveErrorLog(time = self.utilities.getTimeStamp(), errorType = "Buffer", error = f"{e}")
            return False
