from PIL import Image
from models.utilities import Utilities
from ultralytics import YOLO
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

                # ナンバープレートの文字の位置情報を取得して上下の行に分割
                for class_id in range(len(class_ids)):
                    id = int(class_ids[class_id])
                    class_name = self.model.names[id]
                    center_x = (xyxy[class_id][0] + xyxy[class_id][2]) / 2
                    center_y = (xyxy[class_id][1] + xyxy[class_id][3]) / 2

                    if id >= config.OCR_START_REGION_CODE_CLASS_ID:
                        detected_chars.append((class_name, center_x, center_y))

                height = detect_result.height
                center_y = height / 2

                # 二分割した部分をつなげて確認用としてファイル保存
                upper_img = detect_result.crop((0, 0, detect_result.width, int(center_y)))
                lower_img = detect_result.crop((0, int(center_y), detect_result.width, height))

                concat_img = Image.new('RGB', (upper_img.width + lower_img.width, max(upper_img.height, lower_img.height)))
                concat_img.paste(upper_img, (0, 0))
                concat_img.paste(lower_img, (upper_img.width, 0))

                file_name = f"{config.OUTPUT_OCR_DIR}/{Utilities.get_timestamp()}.png"
                concat_img.save(file_name)

                # OCRの検出結果を取得
                for char, x, y in detected_chars:
                    if y < center_y:
                        upper_row_text.append((char, x))
                    else:
                        lower_row_text.append((char, x))

                # ナンバープレートの種類と上下の行の文字をそれぞれソートしてリストに格納
                upper_row_text.sort(key=lambda item: item[1])
                lower_row_text.sort(key=lambda item: item[1])
                upper_row_text = [char for char, _ in upper_row_text]
                lower_row_text = [char for char, _ in lower_row_text]

                return upper_row_text, lower_row_text
        
        return None
