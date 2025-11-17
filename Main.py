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
                self.recognizerController.recognizeNumberPlate(image)

if __name__ == "__main__":
    Main().run()