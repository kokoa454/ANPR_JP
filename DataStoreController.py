__package__ = "DataStoreController"

import CarDBDataStore
import Utilities
import config
import os
import CarBufferDataStore

class DataStoreController:
    def __init__(self):
        self.carDBDataStore = CarDBDataStore.CarDBDataStore()
        self.carBufferDataStore = CarBufferDataStore.CarBufferDataStore()
        self.utilities = Utilities.Utilities()
        os.makedirs(config.OUTPUT_BUFFER_DIR, exist_ok = True)

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

    def insertDataToDB(self, timeStamp: str, numberPlateObject: NumberPlateObject) -> bool:
        data = self._formatData(timeStamp = timeStamp, numberPlateObject = numberPlateObject)
        status = self.carDBDataStore.insertData(timeStamp = timeStamp, data = data)
        return status

    def insertDataToBuffer(self, timeStamp: str, numberPlateObject: NumberPlateObject) -> bool:
        data = self._formatData(timeStamp = timeStamp, numberPlateObject = numberPlateObject)
        status = self.carBufferDataStore.insertData(timeStamp = timeStamp, data = data)
        return status

    def checkBuffer(self) -> bool:
        try:
            with open(f"{self.outputBufferDir}/{self.bufferJsonFileName}", "r") as f:
                return True
        except Exception as e:
            self.error_log.saveErrorLog(time = self.utilities.getTimeStamp(), errorType = "Buffer", error = f"{e}")
            return False

    def insertBufferDataToDB(self) -> bool:
        status, data = self.carBufferDataStore.readData()
        if status == True:
            self._clearBuffer()
            return True
        else:
            return False

    def _clearBuffer(self) -> bool:
        try:
            os.remove(f"{self.outputBufferDir}/{self.bufferJsonFileName}")
            return True
        except Exception as e:
            self.error_log.saveErrorLog(time = self.utilities.getTimeStamp(), errorType = "Buffer", error = f"{e}")
            return False

    def _formatData(self, timeStamp: str, numberPlateObject: NumberPlateObject) -> dict:
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
