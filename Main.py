import DeviceController
import RecognizerController

def main():
    image = DeviceController.DeviceController().processCarDetection()
    if image is not None:
        RecognizerController.RecognizerController().recognizeNumberPlate(image)

if __name__ == "__main__":
    main()