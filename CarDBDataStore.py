__package__ = "CarDBDataStore"

import AbstractCarDataStore
import requests
import ErrorLog
import Utilities
import config

class CarDBDataStore(AbstractCarDataStore.AbstractCarDataStore):
    def __init__(self):
        super().__init__()
        self.error_log = ErrorLog.ErrorLog()
        self.utilities = Utilities.Utilities()
        self.api_connection_check_url = config.API_CONNECTION_CHECK_URL
        self.api_region_code_table_url = config.API_REGION_CODE_TABLE_URL
        self.api_visitors_table_url = config.API_VISITORS_TABLE_URL
        self.api_key = config.API_KEY

    def checkDBConnection(self) -> bool:
        try:
            response = requests.get(url = self.api_connection_check_url, timeout = 5)

            if response.status_code == 200:
                return True
            else:
                self.error_log.saveErrorLog(time = self.utilities.getTimeStamp(), errorType = "DB", error = f"API connection check failed with status code. {response.status_code}")
                return False
        except requests.RequestException as e:
            self.error_log.saveErrorLog(time = self.utilities.getTimeStamp(), errorType = "DB", error = f"{e}")
            return False

    def insertIntoRegionCodeTable(self, data: dict) -> bool:
        try:
            headers = {"x-api-key": self.api_key}
            response = requests.post(url = self.api_region_code_table_url, headers=headers, json=data)

            if response.status_code == 200:
                return True
            else:
                self.error_log.saveErrorLog(time = self.utilities.getTimeStamp(), errorType = "DB", error = f"API connection check failed with status code. {response.status_code}")
                return False
        except requests.RequestException as e:
            self.error_log.saveErrorLog(time = self.utilities.getTimeStamp(), errorType = "DB", error = f"{e}")
            return False

    def insertOrUpdateVisitorsTable(self, data: dict) -> bool:
        try:
            headers = {"x-api-key": self.api_key}
            response = requests.post(url = self.api_visitors_table_url, headers=headers, json=data)

            if response.status_code == 200:
                return True
            else:
                self.error_log.saveErrorLog(time = self.utilities.getTimeStamp(), errorType = "DB", error = f"API connection check failed with status code. {response.status_code}")
                return False
        except requests.RequestException as e:
            self.error_log.saveErrorLog(time = self.utilities.getTimeStamp(), errorType = "DB", error = f"{e}")
            return False
