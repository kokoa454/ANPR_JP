from models.db_datastore import DBDatastore
from models.utilities import Utilities
import config.config as config
import os
from models.buffer_datastore import BufferDatastore
from models.error_log import ErrorLog

class DatastoreController:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self) -> None:
        self.car_db_datastore = DBDatastore.get_instance()
        self.car_buffer_datastore = BufferDatastore.get_instance()

    def insert_data_to_dB(self, timestamp: str) -> bool:
        data = self._formatData(timeStamp = timestamp)
        status = self.car_db_datastore.insert_data(data = data)
        return status
    
    def insert_data_to_buffer(self, timestamp: str) -> bool:
        data = self._formatData(timeStamp = timestamp)
        status = self.car_buffer_datastore.insert_data(data = data)
        return status

    def check_buffer(self) -> bool:
        try:
            if os.path.exists(f"{config.OUTPUT_BUFFER_DIR}/{config.BUFFER_JSON_FILE_NAME}"):
                with open(f"{config.OUTPUT_BUFFER_DIR}/{config.BUFFER_JSON_FILE_NAME}", "r"):
                    return True
        except Exception as e:
            ErrorLog.save_error_log(timestamp = Utilities.get_timestamp_for_local(), error_type = "Buffer", error = f"{e}")
            return False

    def insert_buffer_data_to_db(self) -> bool:
        status, data = self.car_buffer_datastore.read_data()
        if status == True:
            if self.car_db_datastore.insert_buffer_data(data = data) == True:
                self._clear_buffer()
                return True
            else:
                return False
        else:
            return False

    def _clear_buffer(self) -> bool:
        try:
            os.remove(f"{config.OUTPUT_BUFFER_DIR}/{config.BUFFER_JSON_FILE_NAME}")
            return True
        except Exception as e:
            ErrorLog.save_error_log(timestamp = Utilities.get_timestamp_for_local(), error_type = "Buffer", error = f"{e}")
            return False

    def _formatData(self, timeStamp: str) -> dict:

        return {
            "timestamp": timeStamp
        }
