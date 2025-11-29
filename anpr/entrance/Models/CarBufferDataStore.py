import Models.ErrorLog as ErrorLog
import Models.Utilities as Utilities
import config.config as config
import os
import json

class CarBufferDataStore():
    def __init__(self):
        super().__init__()
        self.error_log = ErrorLog.ErrorLog()
        self.utilities = Utilities.Utilities()
        self.outputBufferDir = f"../{config.OUTPUT_BUFFER_DIR}"
        self.bufferJsonFileName = config.BUFFER_JSON_FILE_NAME

    def insertData(self, data: dict) -> bool:
        if os.path.exists(f"{self.outputBufferDir}/{self.bufferJsonFileName}") == False:
            bufferData = []
        else:
            status, bufferData = self.readData()
            if status == False:
                return False
        bufferData.append(data)
        try:
            with open(f"{self.outputBufferDir}/{self.bufferJsonFileName}", "w") as f:
                json.dump(bufferData, f, indent = 4)
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
