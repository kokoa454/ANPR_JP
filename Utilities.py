__package__ = "Utilities"

from datetime import datetime

class Utilities:
    def getTimeStamp(self) -> str:
        now = datetime.now()
        timestamp = now.strftime("%Y_%m_%d_%H_%M_%S")
        return timestamp
