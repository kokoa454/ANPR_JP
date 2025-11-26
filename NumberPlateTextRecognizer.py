__package__ = "NumberPlateTextRecognizer"

from ultralytics import YOLO
import PIL as Image
import config

class NumberPlateTextRecognizer:
    def __init__(self):
        self.model = YOLO(config.OCR_MODEL)

    def detectNPText(self, detectResults: Image.Image) -> tuple[str, list[str], list[str]] | None:
        detectedChars = []
        upperRowText = []
        lowerRowText = []

        # yolo11n-anpr-jp-ocr.ptを使用してナンバープレートの文字を認識
        ocrResults = self.model(
            source = detectResults,
            imgsz = config.OCR_IMG_SIZE,
            conf = config.OCR_CONFIDENCE,
            iou = config.OCR_IOU,
            save = config.OCR_SAVE
        )

        # OCRの検出結果を取得
        classes = ocrResults[0].boxes.cls

        # ナンバープレートの文字が検出された場合の処理
        if len(classes) > 0:
            for ocrResult in ocrResults:
                boxes = ocrResult.boxes
                classIds = boxes.cls
                xyxy = boxes.xyxy

                typeOfVehicleId = int(classes[0])

                # ナンバープレートの文字の位置情報を取得して上下の行に分割
                for classId in range(len(classIds)):
                    id = int(classIds[classId])
                    className = self.model.names[id]
                    centerX = (xyxy[classId][0] + xyxy[classId][2]) / 2
                    centerY = (xyxy[classId][1] + xyxy[classId][3]) / 2

                    if id >= config.OCR_START_REGION_CODE_CLASS_ID:
                        detectedChars.append((className, centerX, centerY))

                height = detectResults.height
                centerY = height / 2

                for char, x, y in detectedChars:
                    if y < centerY:
                        upperRowText.append((char, x))
                    else:
                        lowerRowText.append((char, x))

                # ナンバープレートの種類と上下の行の文字をそれぞれソートしてリストに格納
                typeOfVehicle = self.model.names[typeOfVehicleId]
                upperRowText.sort(key=lambda item: item[1])
                lowerRowText.sort(key=lambda item: item[1])
                upperRowText = [char for char, _ in upperRowText]
                lowerRowText = [char for char, _ in lowerRowText]

                return typeOfVehicle, upperRowText, lowerRowText
        
        return None
