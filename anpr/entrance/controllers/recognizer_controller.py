from models.number_plate import NumberPlate
from models.number_plate_recognizer import NumberPlateRecognizer
from models.number_plate_text_recognizer import NumberPlateTextRecognizer

class RecognizerController:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self.number_plate_recognizer = NumberPlateRecognizer.get_instance()
        self.number_plate_text_recognizer = NumberPlateTextRecognizer.get_instance()

    def recognize_number_plate(self, image: any, number_plate_object: NumberPlate) -> NumberPlate | None:
        detect_result = self.number_plate_recognizer.detect_number_plate(image = image)

        if detect_result is not None:
            print("ナンバープレートを検出しました")
            text_result = self.number_plate_text_recognizer.detect_number_plate_text(detect_result = detect_result)
            if text_result is not None:
                upper_row_text, lower_row_text = text_result[0], text_result[1]
                number_plate_object.format_number_plate_text("".join(upper_row_text), "".join(lower_row_text))
                return number_plate_object
        return None
