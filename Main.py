import DeviceController
import RecognizerController

class Main:
    def __init__(self) -> None:
        self.deviceController = DeviceController.DeviceController()
        self.recognizerController = RecognizerController.RecognizerController()
    
    def run(self) -> None:
        while True:
            image = self.deviceController.processCarDetection()
            if image is not None:
                numberPlateObject = self.recognizerController.recognizeNumberPlate(image)
                if numberPlateObject is not None:
                    print(f"Recognized Number Plate: {numberPlateObject.getTypeOfVehicle()}\n{numberPlateObject.getRegionCode()}{numberPlateObject.getClassNum()} {numberPlateObject.getHiraganaCode()} {numberPlateObject.getRegistNum()}\n")

if __name__ == "__main__":
    Main().run()