# https://gpiozero.readthedocs.io/en/stable/api_input.html
from gpiozero import DistanceSensor
import config.config as config
from models.utilities import Utilities
from models.error_log import ErrorLog

class ProximitySensor:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        try:
            self.sensor = DistanceSensor(
                echo=config.PROXIMITY_SENSOR_ECHO_PIN,
                trigger=config.PROXIMITY_SENSOR_TRIGGER_PIN,
                max_distance=config.PROXIMITY_SENSOR_MAX_DISTANCE_METER,
                )
        except Exception as e:
            ErrorLog.save_error_log(timestamp = Utilities.get_timestamp(), error_type = "ProximitySensor", error = f"{e}")
            self.sensor = None

    def get_distance(self) -> float | None:
        try:
            distance = float(self.sensor.distance) * 100 # convert to centimeter
            return distance
        except Exception as e:
            ErrorLog.save_error_log(timestamp = Utilities.get_timestamp(), error_type = "ProximitySensor", error = f"{e}")
            return None
