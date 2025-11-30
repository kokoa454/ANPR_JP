import requests
from Models.ErrorLog import ErrorLog
from Models.Utilities import Utilities
import config.config as config
import json

class CarDBDataStore:
    _instance = None

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # unused functions
    # def checkDBConnection(self) -> bool:
    #     try:
    #         headers = {self.api_name: self.api_key}
    #         response = requests.get(url = self.api_connection_check_url, headers=headers, timeout = config.DB_CONNECTION_CHECK_TIMEOUT_SEC)

    #         if self._checkRequestStatus(response = response):
    #             return True
    #         else:
    #             return False
    #     except requests.RequestException as e:
    #         self.error_log.saveErrorLog(time = self.utilities.getTimeStamp(), errorType = "DB", error = f"{e}")
    #         return False

    # def insertIntoRegionCodeTable(self, data: dict) -> bool:
    #     try:
    #         headers = {self.api_name: self.api_key}
    #         response = requests.post(url = self.api_region_code_table_url, headers=headers, json=data)

    #         if self._checkRequestStatus(response = response):
    #             return True
    #         else:
    #             return False
    #     except requests.RequestException as e:
    #         self.error_log.saveErrorLog(time = self.utilities.getTimeStamp(), errorType = "DB", error = f"{e}")
    #         return False

    # def insertOrUpdateVisitorsTable(self, data: dict) -> bool:
    #     try:
    #         headers = {self.api_name: self.api_key}
    #         response = requests.post(url = self.api_visitors_table_url, headers=headers, json=data)

    #         if self._checkRequestStatus(response = response):
    #             return True
    #         else:
    #             return False
    #     except requests.RequestException as e:
    #         self.error_log.saveErrorLog(time = self.utilities.getTimeStamp(), errorType = "DB", error = f"{e}")
    #         return False

    def insertData(self, data: dict) -> bool:
        try:
            headers = {config.API_NAME: config.API_KEY}
            response = requests.post(url = config.API_DATA_URL, headers=headers, json=data, timeout = config.DB_TIMEOUT_SEC)

            if self._checkRequestStatus(response = response):
                return True
            else:
                return False
        except requests.RequestException as e:
            ErrorLog.saveErrorLog(time = Utilities.getTimeStamp(), errorType = "DB", error = f"{e}")
            return False

    def insertBufferData(self, data: list[dict]) -> bool:
        try:
            with open(f"{config.OUTPUT_BUFFER_DIR}/{config.BUFFER_JSON_FILE_NAME}", "r") as f:
                data = json.load(f)
                if self.insertData(data = data) == True:
                    return True
                else:
                    return False
        except Exception as e:
            ErrorLog.saveErrorLog(time = Utilities.getTimeStamp(), errorType = "Buffer", error = f"{e}")
            return False

    def _checkRequestStatus(self, response: requests.Response) -> bool:
        if response.status_code == 200:
            return True
        else:
            ErrorLog.saveErrorLog(time = Utilities.getTimeStamp(), errorType = "DB", error = f"API connection check failed with status code. {response.status_code}")
            return False
