# https://gpiozero.readthedocs.io/en/stable/api_input.html
from gpiozero import DistanceSensor
import config.config as config
import Models.Utilities as Utilities
import Models.ErrorLog as ErrorLog

class ProximitySensor:
    def __init__(self) -> None:
        self.utilities = Utilities.Utilities()
        self.errorLog = ErrorLog.ErrorLog()
        self.triggerNum = config.PROXIMITY_SENSOR_TRIGGER_PIN
        self.echoNum = config.PROXIMITY_SENSOR_ECHO_PIN
        self.maxDistanceMeter = config.PROXIMITY_SENSOR_MAX_DISTANCE_METER
        self.outOfRange = config.PROXIMITY_SENSOR_OUT_OF_RANGE

        try:
            self.sensor = DistanceSensor(
                echo=self.echoNum,
                trigger=self.triggerNum,
                max_distance=self.maxDistanceMeter,
                )
        except Exception as e:
            time = self.utilities.getTimeStamp()
            self.errorLog.saveErrorLog(time, "ProximitySensor", f"{e}")
            self.sensor = None

    def getDistance(self) -> float | None:
        try:
            distance = float(self.sensor.distance) * 100 # convert to centimeter
            return distance
        except Exception as e:
            time = self.utilities.getTimeStamp()
            self.errorLog.saveErrorLog(time, "ProximitySensor", f"{e}")
            return None
