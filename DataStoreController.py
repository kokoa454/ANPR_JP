__package__ = "DataStoreController"

import CarDBDataStore
import Utilities
import config

class DataStoreController:
    def __init__(self):
        self.carDBDataStore = CarDBDataStore.CarDBDataStore()
        self.utilities = Utilities.Utilities()

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
        regionCode = numberPlateObject.getRegionCode()
        classNum = numberPlateObject.getClassNum()
        hiraganaCode = numberPlateObject.getHiraganaCode()
        registNum = numberPlateObject.getRegistNum()

        data = self._formatData(timeStamp = timeStamp, regionCode = regionCode, classNum = classNum, hiraganaCode = hiraganaCode, registNum = registNum)
        status = self.carDBDataStore.insertData(timeStamp = timeStamp, data = data)
        return status

    def _formatData(self, timeStamp: str, regionCode: str, classNum: str, hiraganaCode: str, registNum: str) -> dict:
        return {
            "timestamp": timeStamp,
            "region_code": regionCode,
            "class_num": classNum,
            "hiragana_code": hiraganaCode,
            "regist_num": registNum
        }