from datetime import datetime
import config.config as config

class Utilities:
    def __init__(self):
        self.timeStampFormat = config.TIME_STAMP_FORMAT
        self.dayFormat = config.DAY_FORMAT
        self.timeFormat = config.TIME_FORMAT
    
    def getTimeStamp(self) -> str:
        now = datetime.now()
        timestamp = now.strftime(self.timeStampFormat)
        return timestamp

    def getDay(self) -> str:
        now = datetime.now()
        day = now.strftime(self.dayFormat)
        return day

    def getTime(self) -> str:
        now = datetime.now()
        time = now.strftime(self.timeFormat)
        return time