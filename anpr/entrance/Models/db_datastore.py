import requests
from models.error_log import ErrorLog
from models.utilities import Utilities
import config.config as config

class DBDatastore:
    _instance = None

    @classmethod
    def get_instance(cls):
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

    def insert_data(self, data: dict) -> bool:
        try:
            headers = {config.API_NAME: config.API_KEY}
            response = requests.post(url = config.API_DATA_URL, headers=headers, json=data, timeout = config.DB_TIMEOUT_SEC)

            if self._check_request_status(response = response):
                return True
            else:
                return False
        except requests.RequestException as e:
            ErrorLog.save_error_log(timestamp = Utilities.get_timestamp(), error_type = "DB", error = f"{e}")
            return False

    def insert_buffer_data(self, data: list[dict]) -> bool:
        try:
            if self.insert_data(data = data) == True:
                return True
            else:
                return False
        except Exception as e:
            ErrorLog.save_error_log(timestamp = Utilities.get_timestamp(), error_type = "Buffer", error = f"{e}")
            return False

    def _check_request_status(self, response: requests.Response) -> bool:
        if response.status_code == 200:
            return True
        else:
            ErrorLog.save_error_log(timestamp = Utilities.get_timestamp(), error_type = "DB", error = f"API connection check failed with status code. {response.status_code}")
            return False
