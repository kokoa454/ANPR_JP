__package__ = "RecognizerController"

import NumberPlateRecognizer
import NumberPlateTextRecognizer
import NumberPlate

class RecognizerController:
    def __init__(self):
        self.numberPlateRecognizer = NumberPlateRecognizer.NumberPlateRecognizer()
        self.numberPlateTextRecognizer = NumberPlateTextRecognizer.NumberPlateTextRecognizer()

    def recognizeNumberPlate(self, image) -> None:
        detectResults = self.numberPlateRecognizer.detectNP(image)

        if detectResults is not None:
            typeOfVehicle, upperRowText, lowerRowText = self.numberPlateTextRecognizer.detectNPText(detectResults)
            numberPlate = NumberPlate.NumberPlate.formatNPText(typeOfVehicle, upperRowText, lowerRowText)
            print("Recognized Number Plate: ", numberPlate)
            return