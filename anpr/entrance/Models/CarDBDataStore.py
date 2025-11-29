import requests
import Models.ErrorLog as ErrorLog
import Models.Utilities as Utilities
import config.config as config
import json

class CarDBDataStore:
    def __init__(self):
        super().__init__()
        self.error_log = ErrorLog.ErrorLog()
        self.utilities = Utilities.Utilities()
        self.apiDataUrl = config.API_DATA_URL
        self.apiKey = config.API_KEY
        self.apiName = config.API_NAME
        self.outputBufferDir = config.OUTPUT_BUFFER_DIR
        self.bufferJsonFileName = config.BUFFER_JSON_FILE_NAME

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
            headers = {self.apiName: self.apiKey}
            response = requests.post(url = self.apiDataUrl, headers=headers, json=data, timeout = config.DB_TIMEOUT_SEC)

            if self._checkRequestStatus(response = response):
                return True
            else:
                return False
        except requests.RequestException as e:
            self.error_log.saveErrorLog(time = self.utilities.getTimeStamp(), errorType = "DB", error = f"{e}")
            return False

    def insertBufferData(self, data: list[dict]) -> bool:
        try:
            with open(f"{self.outputBufferDir}/{self.bufferJsonFileName}", "r") as f:
                data = json.load(f)
                if self.insertData(data = data) == True:
                    return True
                else:
                    return False
        except Exception as e:
            self.error_log.saveErrorLog(time = self.utilities.getTimeStamp(), errorType = "Buffer", error = f"{e}")
            return False

    def _checkRequestStatus(self, response: requests.Response) -> bool:
        if response.status_code == 200:
            return True
        else:
            self.error_log.saveErrorLog(time = self.utilities.getTimeStamp(), errorType = "DB", error = f"API connection check failed with status code. {response.status_code}")
            return False
