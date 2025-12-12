import json
import os
import config.config as config
from models.error_log import ErrorLog
from models.utilities import Utilities

class BufferDatastore:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def insert_data(self, data: dict) -> bool:
        if os.path.exists(f"{config.OUTPUT_BUFFER_DIR}/{config.BUFFER_JSON_FILE_NAME}") == False:
            buffer_data = []
        else:
            status, buffer_data = self.read_data()
            if status == False:
                return False
        buffer_data.append(data)
        
        try:
            with open(f"{config.OUTPUT_BUFFER_DIR}/{config.BUFFER_JSON_FILE_NAME}", "w") as f:
                json.dump(buffer_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            ErrorLog.save_error_log(timestamp = Utilities.get_timestamp_for_local(), error_type = "Buffer", error = f"{e}")
            return False
    
    def read_data(self) -> tuple[bool, list[dict]]:
        try:
            with open(f"{config.OUTPUT_BUFFER_DIR}/{config.BUFFER_JSON_FILE_NAME}", "r") as f:
                data = json.load(f)
                return True, data
        except Exception as e:
            ErrorLog.save_error_log(timestamp = Utilities.get_timestamp_for_local(), error_type = "Buffer", error = f"{e}")
            return False, None
