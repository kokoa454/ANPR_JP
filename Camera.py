__package__ = "Camera"

from PIL import Image
import cv2

CAMERA_ID = 0

class Camera:
    def __init__(self):
        pass

    def _openCamera(self):
        capture = cv2.VideoCapture(CAMERA_ID)
        return capture
            
    def _closeCamera(self, capture):
        capture.release()
        cv2.destroyAllWindows()

    def captureImage(self):
        try:
            capture = self._openCamera()
            ret, frame = capture.read()
            self._closeCamera(capture)

            if ret:
                return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        except Exception as e:
            print(f"ERROR: {e}")
        return None
