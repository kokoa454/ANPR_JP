from models.db_datastore import DBDatastore
from models.utilities import Utilities
import config.config as config
import os
from models.buffer_datastore import BufferDatastore
from models.number_plate import NumberPlate
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

    # unused functions
    # def checkDBConnection(self) -> bool:
    #     return self.carDBDataStore.checkDBConnection()

    # def _formatRegionCodeTableData(self, day: str, time: str, regionCode: str) -> dict:
    #     return {
    #         "day": day,
    #         "time": time,
    #         "region_code": regionCode
    #     }   

    # def _formatVisitorsTableData(self, day: str) -> dict:
    #     return {
    #         "day": day,
    #     }

    # def insertIntoRegionCodeTable(self, day: str, time: str, regionCode: str) -> bool:
    #     data = self._formatRegionCodeTableData(day = day, time = time, regionCode = regionCode)
    #     return self.carDBDataStore.insertIntoRegionCodeTable(data)

    # def insertOrUpdateVisitorsTable(self, day: str) -> bool:
    #     data = self._formatVisitorsTableData(day = day)
    #     return self.carDBDataStore.insertOrUpdateVisitorsTable(data)

    def insert_data_to_dB(self, timestamp: str, number_plate_object: NumberPlate) -> bool:
        data = self._formatData(timeStamp = timestamp, number_plate_object = number_plate_object)
        status = self.car_db_datastore.insert_data(data = data)
        return status
    
    def insert_data_to_buffer(self, timestamp: str, number_plate_object: NumberPlate) -> bool:
        data = self._formatData(timeStamp = timestamp, number_plate_object = number_plate_object)
        status = self.car_buffer_datastore.insert_data(data = data)
        return status

    def check_buffer(self) -> bool:
        try:
            with open(f"{config.OUTPUT_BUFFER_DIR}/{config.BUFFER_JSON_FILE_NAME}", "r"):
                return True
        except Exception as e:
            ErrorLog.save_error_log(timestamp = Utilities.get_timestamp(), error_type = "Buffer", error = f"{e}")
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
            ErrorLog.save_error_log(timestamp = Utilities.get_timestamp(), error_type = "Buffer", error = f"{e}")
            return False

    def _formatData(self, timeStamp: str, number_plate_object: NumberPlate) -> dict:
        region_code = number_plate_object.get_region_code()
        class_num = number_plate_object.get_class_num()
        hiragana_code = number_plate_object.get_hiragana_code()
        regist_num = number_plate_object.get_regist_num()

        return {
            "timestamp": timeStamp,
            "region_code": region_code,
            "class_num": class_num,
            "hiragana_code": hiragana_code,
            "regist_num": regist_num
        }
