import DeviceController
import RecognizerController
import config
import time

class Main:
    def __init__(self) -> None:
        self.deviceController = DeviceController.DeviceController()
        self.recognizerController = RecognizerController.RecognizerController()
        self.carDetected = False
        self.detectionPaused = False
    
    def run(self) -> None:
        while True:
            self.carDetected = self.deviceController.detectCar()

            if self.carDetected == False and self.detectionPaused == True:
                self.detectionPaused = False

            elif self.carDetected == True and self.detectionPaused == False:
                self.detectionPaused = True

                image = self.deviceController.captureNumberPlate()

                if image is not None:
                    numberPlateObject = self.recognizerController.recognizeNumberPlate(image)

                    if numberPlateObject is not None:
                        print(f"Recognized Number Plate: {numberPlateObject.getTypeOfVehicle()}\n{numberPlateObject.getRegionCode()}{numberPlateObject.getClassNum()} {numberPlateObject.getHiraganaCode()} {numberPlateObject.getRegistNum()}\n")
                
            time.sleep(config.MAIN_LOOP_DELAY_SEC)

if __name__ == "__main__":
    Main().run()
