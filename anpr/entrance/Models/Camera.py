from PIL import Image
import Models.Utilities as Utilities
import Models.ErrorLog as ErrorLog
import cv2
import os
import config.config as config

class Camera:
    def __init__(self):
        self.utilities = Utilities.Utilities()
        self.errorLog = ErrorLog.ErrorLog()
        self.outputCaptureDir = config.OUTPUT_CAPTURE_DIR
        self.rpicamMetering = config.RPICAM_METERING
        self.rpicamAutoFocusMode = config.RPICAM_AUTOFOCUS_MODE
        self.rpicamTimeout = config.RPICAM_TIMEOUT

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
            fileName = f"{self.outputCaptureDir}/captured_image_{self.utilities.getTimeStamp()}.jpeg"
            os.system(f"rpicam-jpeg --metering {self.rpicamMetering} -n --autofocus-mode {self.rpicamAutoFocusMode} --output {fileName} --timeout {self.rpicamTimeout}")
            return Image.open(fileName)
        except Exception as e:
            time = self.utilities.getTimeStamp()
            self.errorLog.saveErrorLog(time = time, errorType = "Camera", error = f"{e}")
            return None
