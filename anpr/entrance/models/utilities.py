from datetime import datetime
import config.config as config

class Utilities:
    @staticmethod
    def get_timestamp() -> str:
        now = datetime.now()
        timestamp = now.strftime(config.TIME_STAMP_FORMAT)
        return timestamp

    @staticmethod
    def get_day() -> str:
        now = datetime.now()
        day = now.strftime(config.DAY_FORMAT)
        return day

    @staticmethod
    def get_time() -> str:
        now = datetime.now()
        time = now.strftime(config.TIME_FORMAT)
        return time