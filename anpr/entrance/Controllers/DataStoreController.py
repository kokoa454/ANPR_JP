from Models.CarDBDataStore import CarDBDataStore
from Models.Utilities import Utilities
import config.config as config
import os
from Models.CarBufferDataStore import CarBufferDataStore
from Models.NumberPlate import NumberPlate
from Models.ErrorLog import ErrorLog

class DataStoreController:
    _instance = None

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self.carDBDataStore = CarDBDataStore.getInstance()
        self.carBufferDataStore = CarBufferDataStore.getInstance()

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

    def insertDataToDB(self, timeStamp: str, numberPlateObject: NumberPlate) -> bool:
        data = self._formatData(timeStamp = timeStamp, numberPlateObject = numberPlateObject)
        status = self.carDBDataStore.insertData(data = data)
        return status

    def insertDataToBuffer(self, timeStamp: str, numberPlateObject: NumberPlate) -> bool:
        data = self._formatData(timeStamp = timeStamp, numberPlateObject = numberPlateObject)
        status = self.carBufferDataStore.insertData(data = data)
        return status

    def checkBuffer(self) -> bool:
        try:
            with open(f"{config.BUFFER_DIR}/{config.BUFFER_JSON_FILE_NAME}", "r"):
                return True
        except Exception as e:
            ErrorLog.saveErrorLog(time = Utilities.getTimeStamp(), errorType = "Buffer", error = f"{e}")
            return False

    def insertBufferDataToDB(self) -> bool:
        status, data = self.carBufferDataStore.readData()
        if status == True:
            if self.carDBDataStore.insertBufferData(data = data) == True:
                self._clearBuffer()
                return True
            else:
                return False
        else:
            return False

    def _clearBuffer(self) -> bool:
        try:
            os.remove(f"{config.BUFFER_DIR}/{config.BUFFER_JSON_FILE_NAME}")
            return True
        except Exception as e:
            ErrorLog.saveErrorLog(time = Utilities.getTimeStamp(), errorType = "Buffer", error = f"{e}")
            return False

    def _formatData(self, timeStamp: str, numberPlateObject: NumberPlate) -> dict:
        regionCode = numberPlateObject.getRegionCode()
        classNum = numberPlateObject.getClassNum()
        hiraganaCode = numberPlateObject.getHiraganaCode()
        registNum = numberPlateObject.getRegistNum()

        return {
            "timestamp": timeStamp,
            "region_code": regionCode,
            "class_num": classNum,
            "hiragana_code": hiraganaCode,
            "regist_num": registNum
        }
