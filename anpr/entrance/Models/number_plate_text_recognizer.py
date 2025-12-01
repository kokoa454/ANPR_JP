from ultralytics import YOLO
from PIL import Image
import config.config as config

class NumberPlateTextRecognizer:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self.model = YOLO(model = config.OCR_MODEL)
    
    def detect_number_plate_text(self, detect_result: Image.Image) -> tuple[str, list[str], list[str]] | None:
        detected_chars = []
        upper_row_text = []
        lower_row_text = []

        # yolo11n-anpr-jp-ocr.ptを使用してナンバープレートの文字を認識
        ocr_result = self.model(
            source = detect_result,
            imgsz = config.OCR_IMG_SIZE,
            conf = config.OCR_CONFIDENCE,
            iou = config.OCR_IOU,
            save = config.OCR_SAVE
        )

        # OCRの検出結果を取得
        classes = ocr_result[0].boxes.cls

        # ナンバープレートの文字が検出された場合の処理
        if len(classes) > 0:
            for result in ocr_result:
                boxes = result.boxes
                class_ids = boxes.cls
                xyxy = boxes.xyxy

                type_of_vehicle_id = int(classes[0])

                # ナンバープレートの文字の位置情報を取得して上下の行に分割
                for class_id in range(len(class_ids)):
                    id = int(class_ids[class_id])
                    class_name = ocr_result.names[id]
                    center_x = (xyxy[class_id][0] + xyxy[class_id][2]) / 2
                    center_y = (xyxy[class_id][1] + xyxy[class_id][3]) / 2

                    if id >= config.OCR_START_REGION_CODE_CLASS_ID:
                        detected_chars.append((class_name, center_x, center_y))

                height = detect_result.height
                center_y = height / 2

                for char, x, y in detected_chars:
                    if y < center_y:
                        upper_row_text.append((char, x))
                    else:
                        lower_row_text.append((char, x))

                # ナンバープレートの種類と上下の行の文字をそれぞれソートしてリストに格納
                type_of_vehicle = ocr_result.names[type_of_vehicle_id]
                upper_row_text.sort(key=lambda item: item[1])
                lower_row_text.sort(key=lambda item: item[1])
                upper_row_text = [char for char, _ in upper_row_text]
                lower_row_text = [char for char, _ in lower_row_text]

                return type_of_vehicle, upper_row_text, lower_row_text
        
        return None
