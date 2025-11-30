# https://gpiozero.readthedocs.io/en/stable/api_input.html
from gpiozero import DistanceSensor
import config.config as config
from Models.Utilities import Utilities
from Models.ErrorLog import ErrorLog

class ProximitySensor:
    _instance = None

    @classmethod
    def getInstance(cls):
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
            time = Utilities.getTimeStamp()
            ErrorLog.saveErrorLog(time, "ProximitySensor", f"{e}")
            self.sensor = None

    def getDistance(self) -> float | None:
        try:
            distance = float(self.sensor.distance) * 100 # convert to centimeter
            return distance
        except Exception as e:
            time = Utilities.getTimeStamp()
            ErrorLog.saveErrorLog(time, "ProximitySensor", f"{e}")
            return None
