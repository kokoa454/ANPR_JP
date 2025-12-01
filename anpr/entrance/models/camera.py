from PIL import Image
from models.utilities import Utilities
from models.error_log import ErrorLog
import config.config as config
import subprocess

class Camera:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    #-- opencv is not used due to errors with opening the camera
    # def _openCamera(self):
    #     capture = cv2.VideoCapture(config.CAMERA_ID)
    #     return capture
    
    # def _closeCamera(self, capture):
    #     capture.release()

    # def captureImage(self):
    #     try:
    #         capture = self._openCamera()
    #         ret, frame = capture.read()
    #         self._closeCamera(capture)

    #         if ret:
    #             fileName = f"./outputs/capture/captured_image_{self.utilities.getTimeStamp()}.jpeg"
    #             cv2.imwrite(fileName, frame)
    #             return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    #     except Exception as e:
    #         self.errorLog.saveErrorLog(f"Camera: {e}")
    #         return None

    # changed to use subprocess
    # def captureImage(self) -> Image.Image | None:
    #     try:
    #         fileName = f"{config.OUTPUT_CAPTURE_DIR}/captured_image_{Utilities.getTimeStamp()}.jpeg"
    #         os.system(f"rpicam-jpeg --metering {config.RPICAM_METERING} -n --autofocus-mode {config.RPICAM_AUTOFOCUS_MODE} --output {fileName} --timeout {config.RPICAM_TIMEOUT}")
    #         return Image.open(fileName)
    #     except Exception as e:
    #         ErrorLog.saveErrorLog(time = Utilities.getTimeStamp(), errorType = "Camera", error = f"{e}")
    #         return None

    def capture_image(self) -> Image.Image | None:
        file_name = f"{config.OUTPUT_CAPTURE_DIR}/captured_image_{Utilities.get_timestamp()}.jpeg"
        command = [
            "rpicam-jpeg",
            "--metering", config.RPICAM_METERING,
            "-n",
            "--autofocus-mode", config.RPICAM_AUTOFOCUS_MODE,
            "--output", file_name,
            "--timeout", config.RPICAM_TIMEOUT
        ]
        
        try:
            subprocess.run(command, check=True)
            return Image.open(file_name)
        except Exception as e:
            ErrorLog.save_error_log(timestamp = Utilities.get_timestamp(), error_type = "Camera", error = f"{e}")
            return None
