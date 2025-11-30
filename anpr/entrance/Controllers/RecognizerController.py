from Models.NumberPlateRecognizer import NumberPlateRecognizer
from Models.NumberPlateTextRecognizer import NumberPlateTextRecognizer
from Models.NumberPlate import NumberPlate
import os
import config.config as config

class RecognizerController:
    _instance = None

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self.numberPlateRecognizer = NumberPlateRecognizer.getInstance()
        self.numberPlateTextRecognizer = NumberPlateTextRecognizer.getInstance()

    def recognizeNumberPlate(self, image: any, numberPlateObject: NumberPlate) -> NumberPlate | None:
        detectResults = self.numberPlateRecognizer.detectNP(image = image)

        if detectResults is not None:
            typeOfVehicle, upperRowText, lowerRowText = self.numberPlateTextRecognizer.detectNPText(detectResults = detectResults)
            numberPlateObject.formatNPText(typeOfVehicle, "".join(upperRowText), "".join(lowerRowText))
            return numberPlateObject
        return None
