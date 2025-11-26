__package__ = "DataStoreController"

import CarDBDataStore
import Utilities
import config

class DataStoreController:
    def __init__(self):
        self.car_db_data_store = CarDBDataStore.CarDBDataStore()
        self.utilities = Utilities.Utilities()

    def checkDBConnection(self) -> bool:
        return self.car_db_data_store.checkDBConnection()

    def _formatRegionCodeTableData(self, day: str, time: str, regionCode: str) -> dict:
        return {
            "day": day,
            "time": time,
            "region_code": regionCode
        }   

    def _formatVisitorsTableData(self, day: str) -> dict:
        return {
            "day": day,
        }

    def insertIntoRegionCodeTable(self, day: str, time: str, regionCode: str) -> bool:
        data = self._formatRegionCodeTableData(day = day, time = time, regionCode = regionCode)
        return self.car_db_data_store.insertIntoRegionCodeTable(data)

    def insertOrUpdateVisitorsTable(self, day: str) -> bool:
        data = self._formatVisitorsTableData(day = day)
        return self.car_db_data_store.insertOrUpdateVisitorsTable(data)
