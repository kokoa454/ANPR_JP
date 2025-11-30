from PIL import Image
from Models.Utilities import Utilities
from Models.ErrorLog import ErrorLog
import cv2
import os
import config.config as config

class Camera:
    _instance = None

    @classmethod
    def getInstance(cls):
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

    def captureImage(self) -> Image.Image | None:
        try:
            fileName = f"{config.OUTPUT_CAPTURE_DIR}/captured_image_{Utilities.getTimeStamp()}.jpeg"
            os.system(f"rpicam-jpeg --metering {config.RPICAM_METERING} -n --autofocus-mode {config.RPICAM_AUTOFOCUS_MODE} --output {fileName} --timeout {config.RPICAM_TIMEOUT}")
            return Image.open(fileName)
        except Exception as e:
            ErrorLog.saveErrorLog(time = Utilities.getTimeStamp(), errorType = "Camera", error = f"{e}")
            return None
