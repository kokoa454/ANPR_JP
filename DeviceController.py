__package__ = "DeviceController"

import os
from Camera import Camera
import PIL.Image as Image
import config

class DeviceController:
    def __init__(self):
        self.camera = Camera()
        os.makedirs(config.OUTPUT_CAPTURE_DIR, exist_ok=True)      

    def processCarDetection(self) -> Image.Image | None:
        inputKey = input("enter c to capture an image from the camera: ")
        if inputKey == "c":
            image = self.camera.captureImage()
            return image
        return None
