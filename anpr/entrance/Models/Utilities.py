from datetime import datetime
import config.config as config

class Utilities:
    def getTimeStamp(self) -> str:
        now = datetime.now()
        timestamp = now.strftime(config.TIME_STAMP_FORMAT)
        return timestamp

    def getDay(self) -> str:
        now = datetime.now()
        day = now.strftime(config.DAY_FORMAT)
        return day

    def getTime(self) -> str:
        now = datetime.now()
        time = now.strftime(config.TIME_FORMAT)
        return time