import os
from Models.Camera import Camera
from Models.ProximitySensor import ProximitySensor
import PIL.Image as Image
import config.config as config

class DeviceController:
    _instance = None

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self.camera = Camera.getInstance()
        self.proximitySensor = ProximitySensor.getInstance()
    
    def detectCar(self) -> bool:
        distance = self.proximitySensor.getDistance()
        
        if distance is not None and distance < config.PROXIMITY_SENSOR_MAX_DISTANCE_METER * 100:
            print(f"ProximitySensor: Measured Distance = {distance} cm")
            return True
        else:
            distance = config.PROXIMITY_SENSOR_OUT_OF_RANGE
            print(f"ProximitySensor: Measured Distance = {distance} cm")
            return False

    def captureNumberPlate(self) -> Image.Image | None:
        image = self.camera.captureImage()
        return image
