from datetime import datetime
import config.config as config

class Utilities:
    @staticmethod
    def get_timestamp_for_db() -> str:
        now = datetime.now()
        timestamp = now.strftime(config.TIME_STAMP_DB_FORMAT)
        return timestamp
    
    @staticmethod
    def get_timestamp_for_local() -> str:
        now = datetime.now()
        timestamp = now.strftime(config.TIME_STAMP_LOCAL_FORMAT)
        return timestamp
