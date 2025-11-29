__package__ = "RecognizerController"

import anpr.entrance.Module.NumberPlateRecognizer as NumberPlateRecognizer
import anpr.entrance.Module.NumberPlateTextRecognizer as NumberPlateTextRecognizer
import anpr.entrance.Module.NumberPlate as NumberPlate
import os
import config

class RecognizerController:
    def __init__(self):
        self.numberPlateRecognizer = NumberPlateRecognizer.NumberPlateRecognizer()
        self.numberPlateTextRecognizer = NumberPlateTextRecognizer.NumberPlateTextRecognizer()
        os.makedirs(config.OUTPUT_DETECT_DIR, exist_ok=True)

    def recognizeNumberPlate(self, image: any, numberPlateObject: NumberPlate.NumberPlate) -> NumberPlate.NumberPlate | None:
        detectResults = self.numberPlateRecognizer.detectNP(image = image)

        if detectResults is not None:
            typeOfVehicle, upperRowText, lowerRowText = self.numberPlateTextRecognizer.detectNPText(detectResults = detectResults)
            numberPlateObject.formatNPText(typeOfVehicle, "".join(upperRowText), "".join(lowerRowText))
            return numberPlateObject
        return None
