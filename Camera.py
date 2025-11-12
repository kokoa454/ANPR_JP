__package__ = "Camera"

import cv2

class Camera:
    def __init__(self):
        pass

    def _openCamera(self, camera_id: int):
        capture = cv2.VideoCapture(camera_id)
        return capture

    def _closeCamera(self, capture):
        capture.release()
        cv2.destroyAllWindows()

    def captureImage(self, camera_id: int):
        try:
            capture = self._openCamera(camera_id)
            ret, frame = capture.read()
            self._closeCamera(capture)
            if ret:
                return frame
        except Exception as e:
            print(f"ERROR: {e}")
        return None
