import os
from PIL import Image
import config.config as config
from models.error_log import ErrorLog
from models.utilities import Utilities

class Camera:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def capture_image(self) -> Image.Image | None:
        try:
            file_name = f"{config.OUTPUT_CAPTURE_DIR}/{Utilities.get_timestamp()}.jpeg"
            os.system(f"rpicam-still --hdr --zsl --metering {config.RPICAM_METERING} -n --autofocus-mode {config.RPICAM_AUTOFOCUS_MODE} --output {file_name} --timeout {config.RPICAM_TIMEOUT}")
            return Image.open(file_name)
        except Exception as e:
            ErrorLog.save_error_log(timestamp = Utilities.get_timestamp(), error_type = "Camera", error = f"{e}")
            return None
