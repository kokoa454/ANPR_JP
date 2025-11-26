__package__ = "DeviceController"

import os
from Camera import Camera
from ProximitySensor import ProximitySensor
import PIL.Image as Image
import config

class DeviceController:
    def __init__(self):
        self.camera = Camera()
        self.proximitySensor = ProximitySensor()
        self.outOfRange = config.PROXIMITY_SENSOR_OUT_OF_RANGE
        os.makedirs(path = config.OUTPUT_CAPTURE_DIR, exist_ok = True)

    def detectCar(self) -> bool:
        distance = self.proximitySensor.getDistance()
        
        if distance is not None and distance <= self.outOfRange:
            print(f"ProximitySensor: Measured Distance = {distance} cm")
            return True
        else:
            distance = self.outOfRange
            print(f"ProximitySensor: Measured Distance = {distance} cm")
            return False

    def captureNumberPlate(self) -> Image.Image | None:
        image = self.camera.captureImage()
        return image
