__package__ = "RecognizerController"

import NumberPlateRecognizer
import NumberPlateTextRecognizer
import NumberPlate
import os
import config

class RecognizerController:
    def __init__(self):
        self.numberPlateRecognizer = NumberPlateRecognizer.NumberPlateRecognizer()
        self.numberPlateTextRecognizer = NumberPlateTextRecognizer.NumberPlateTextRecognizer()
        os.makedirs(config.OUTPUT_DETECT_DIR, exist_ok=True)

    def recognizeNumberPlate(self, image) -> NumberPlate.NumberPlate | None:
        detectResults = self.numberPlateRecognizer.detectNP(image)

        if detectResults is not None:
            typeOfVehicle, upperRowText, lowerRowText = self.numberPlateTextRecognizer.detectNPText(detectResults)
            numberPlateObject = NumberPlate.NumberPlate()
            numberPlateObject.formatNPText(typeOfVehicle, "".join(upperRowText), "".join(lowerRowText))
            return numberPlateObject
        return None
