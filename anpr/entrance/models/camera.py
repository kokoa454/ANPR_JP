import os
from PIL import Image
import config.config as config
from models.error_log import ErrorLog
from models.utilities import Utilities
from models.notification import Notification

class Camera:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def capture_image(self) -> tuple[Image.Image | None, str | None]:
        try:
            file_path = f"{config.OUTPUT_CAPTURE_DIR}/{Utilities.get_timestamp()}.jpeg"
            os.system(f"rpicam-still --hdr --zsl --metering {config.RPICAM_METERING} -n --autofocus-mode {config.RPICAM_AUTOFOCUS_MODE} --output {file_path} --timeout {config.RPICAM_TIMEOUT}")
            return Image.open(file_path), file_path
        except Exception as e:
            timestamp = Utilities.get_timestamp()
            ErrorLog.save_error_log(timestamp = timestamp, error_type = "Camera", error = f"{e}")
            Notification.send_error_notification(timestamp = timestamp, error_type = "Camera", error = f"{e}")
            return None, None
