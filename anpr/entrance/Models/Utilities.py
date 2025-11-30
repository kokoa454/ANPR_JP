from datetime import datetime
import config.config as config

class Utilities:
    @staticmethod
    def getTimeStamp() -> str:
        now = datetime.now()
        timestamp = now.strftime(config.TIME_STAMP_FORMAT)
        return timestamp

    @staticmethod
    def getDay() -> str:
        now = datetime.now()
        day = now.strftime(config.DAY_FORMAT)
        return day

    @staticmethod
    def getTime() -> str:
        now = datetime.now()
        time = now.strftime(config.TIME_FORMAT)
        return time