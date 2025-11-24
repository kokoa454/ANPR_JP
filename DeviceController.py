__package__ = "DeviceController"

import os
from Camera import Camera
from ProximitySensor import ProximitySensor
import PIL.Image as Image
import config

class DeviceController:
    def __init__(self):
        self.camera = camera if camera else Camera()
        self.proximitySensor = ProximitySensor()
        os.makedirs(config.OUTPUT_CAPTURE_DIR, exist_ok=True)

    def detectCar(self) -> float | None:
        distance = self.proximitySensor.getDistance()
        
        if distance is not None and distance < config.PROXIMITY_SENSOR_THRESHOLD_CM:
            return distance
        else:
            return None

    def captureNP(self) -> Image.Image | None:
        image = self.camera.captureImage()
        return image
    
    def resumeCarDetection(self) -> None:
        self.proximitySensor.openSensor()

    def pauseCarDetection(self) -> None:
        self.proximitySensor.closeSensor()
