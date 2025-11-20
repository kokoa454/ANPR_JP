__package__ = "Utilities"

from datetime import datetime
import config

class Utilities:
    def getTimeStamp(self) -> str:
        now = datetime.now()
        timestamp = now.strftime(config.TIME_STAMP_FORMAT)
        return timestamp
