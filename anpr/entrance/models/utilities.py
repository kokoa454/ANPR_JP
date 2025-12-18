from datetime import datetime
import config.config as config

class Utilities:
    @staticmethod
    def get_timestamp() -> str:
        now = datetime.now()
        timestamp = now.strftime(config.TIME_STAMP_DB_FORMAT)
        return timestamp
