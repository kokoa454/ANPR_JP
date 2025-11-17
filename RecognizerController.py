__package__ = "RecognizerController"

import NumberPlateRecognizer
import NumberPlateTextRecognizer
import NumberPlate
import os

class RecognizerController:
    def __init__(self):
        self.numberPlateRecognizer = NumberPlateRecognizer.NumberPlateRecognizer()
        self.numberPlateTextRecognizer = NumberPlateTextRecognizer.NumberPlateTextRecognizer()
        os.makedirs("./outputs/detect", exist_ok=True)

    def recognizeNumberPlate(self, image):
        detectResults = self.numberPlateRecognizer.detectNP(image)

        if detectResults is not None:
            typeOfVehicle, upperRowText, lowerRowText = self.numberPlateTextRecognizer.detectNPText(detectResults)
            numberPlateObject = NumberPlate.NumberPlate()
            numberPlateObject.formatNPText(typeOfVehicle, "".join(upperRowText), "".join(lowerRowText))
            print(f"Recognized Number Plate: {numberPlateObject.getTypeOfVehicle()}\n{numberPlateObject.getRegionCode()}{numberPlateObject.getClassNum()} {numberPlateObject.getHiraganaCode()} {numberPlateObject.getRegistNum()}\n")
            return numberPlateObject
        return None
