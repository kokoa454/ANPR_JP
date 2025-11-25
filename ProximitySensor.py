__package__ = "ProximitySensor"

# https://gpiozero.readthedocs.io/en/stable/api_input.html
from gpiozero import DistanceSensor
import config
import Utilities
import ErrorLog

class ProximitySensor:
    def __init__(self) -> None:
        self.utilities = Utilities.Utilities()
        self.errorLog = ErrorLog.ErrorLog()
        self.triggerNum = config.PROXIMITY_SENSOR_TRIGGER_PIN
        self.echoNum = config.PROXIMITY_SENSOR_ECHO_PIN

        try:
            self.sensor = DistanceSensor(echo=self.echoNum, trigger=self.triggerNum)
        except Exception as e:
            time = self.utilities.getTimeStamp()
            self.errorLog.saveErrorLog(time, "ProximitySensor", f"{e}")
            self.sensor = None

    def getDistance(self) -> float | None:
        try:
            distance = self.sensor.distance * 100 # convert to centimeters
            print(f"ProximitySensor: Measured Distance = {distance} cm")
            return distance
        except Exception as e:
            time = self.utilities.getTimeStamp()
            self.errorLog.saveErrorLog(time, "ProximitySensor", f"{e}")
            return None
