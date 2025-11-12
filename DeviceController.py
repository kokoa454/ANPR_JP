__package__ = "DeviceController"

from Camera import Camera
import PIL.Image as Image

class DeviceController:
    def __init__(self):
        self.camera = Camera()

    def processCarDetection(self) -> Image.Image | None:
        inputKey = input("Press c to capture an image from the camera...")
        if inputKey == "c":
            image = self.camera.captureImage()
            return image
        return None