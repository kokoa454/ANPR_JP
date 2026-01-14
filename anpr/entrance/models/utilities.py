from datetime import datetime
import config.config as config

class Utilities:
    @staticmethod
    def get_timestamp() -> str:
        now = datetime.now()
        timestamp = now.strftime(config.TIME_STAMP_FORMAT)
        return timestamp

    @staticmethod
    def get_date() -> str:
        now = datetime.now()
        date = now.strftime(config.DATE_FORMAT)
        return date
