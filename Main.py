import DeviceController
import RecognizerController
import config
import time

class Main:
    def __init__(self) -> None:
        self.deviceController = DeviceController.DeviceController()
        self.recognizerController = RecognizerController.RecognizerController()
    
    def run(self) -> None:
        while True:
            distance = self.deviceController.detectCar()
            if distance is not None:
                self.deviceController.pauseCarDetection()
                image = self.deviceController.captureNP()

                if image is not None:
                    numberPlateObject = self.recognizerController.recognizeNumberPlate(image)

                    if numberPlateObject is not None:
                        print(f"Recognized Number Plate: {numberPlateObject.getTypeOfVehicle()}\n{numberPlateObject.getRegionCode()}{numberPlateObject.getClassNum()} {numberPlateObject.getHiraganaCode()} {numberPlateObject.getRegistNum()}\n")
                
                self.deviceController.resumeCarDetection()
            time.sleep(config.PROXIMITY_SENSOR_TRIGGER_WAIT_SEC)

if __name__ == "__main__":
    Main().run()
