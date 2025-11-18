__package__ = "Camera"

from PIL import Image
import Utilities
import ErrorLog
import cv2
import os

CAMERA_ID = 0

class Camera:
    def __init__(self):
        self.utilities = Utilities.Utilities()
        self.errorLog = ErrorLog.ErrorLog()

    #-- opencv is not used due to errors with opening the camera
    # def _openCamera(self):
    #     capture = cv2.VideoCapture(CAMERA_ID)
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
            fileName = f"./outputs/capture/captured_image_{self.utilities.getTimeStamp()}.jpeg"
            os.system(f"rpicam-jpeg --metering spot -n --autofocus-mode continuous --output {fileName} --timeout 2000")
            return Image.open(fileName)
        except Exception as e:
            self.errorLog.saveErrorLog(f"Camera: {e}")
            return None