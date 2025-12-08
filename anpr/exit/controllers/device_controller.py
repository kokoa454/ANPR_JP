from models.proximity_sensor import ProximitySensor
import config.config as config

class DeviceController:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self.proximity_sensor = ProximitySensor.get_instance()
    
    def detect_car(self) -> bool:
        distance = self.proximity_sensor.get_distance()
        
        if distance is not None and distance < config.PROXIMITY_SENSOR_MAX_DISTANCE_METER * 100:
            print(f"検知距離: {distance} cm")
            return True
        else:
            distance = config.PROXIMITY_SENSOR_OUT_OF_RANGE
            print(f"検知距離: {distance} cm")
            return False
