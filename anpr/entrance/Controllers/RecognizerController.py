import Models.NumberPlateRecognizer as NumberPlateRecognizer
import Models.NumberPlateTextRecognizer as NumberPlateTextRecognizer
import Models.NumberPlate as NumberPlate
import os
import config.config as config

class RecognizerController:
    def __init__(self):
        self.numberPlateRecognizer = NumberPlateRecognizer.NumberPlateRecognizer()
        self.numberPlateTextRecognizer = NumberPlateTextRecognizer.NumberPlateTextRecognizer()
        self.outputDetectDir = f"../{config.OUTPUT_DETECT_DIR}"
        os.makedirs(self.outputDetectDir, exist_ok=True)

    def recognizeNumberPlate(self, image: any, numberPlateObject: NumberPlate.NumberPlate) -> NumberPlate.NumberPlate | None:
        detectResults = self.numberPlateRecognizer.detectNP(image = image)

        if detectResults is not None:
            typeOfVehicle, upperRowText, lowerRowText = self.numberPlateTextRecognizer.detectNPText(detectResults = detectResults)
            numberPlateObject.formatNPText(typeOfVehicle, "".join(upperRowText), "".join(lowerRowText))
            return numberPlateObject
        return None
