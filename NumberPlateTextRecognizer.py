__package__ = "NumberPlateTextRecognizer"

from ultralytics import YOLO
import PIL.Image as Image

class NumberPlateTextRecognizer:
    def __init__(self):
        self.model = YOLO("yolo11n-anpr-jp-ocr.pt")

    def detectNPText(self, detectResults: Image) -> tuple[str, list[tuple[str, float]], list[tuple[str, float]]]:
        ocrResults = self.model(
            source = detectResults,
            imgsz = 640,
            conf = 0.5,
            iou = 0.3,
            save = False
        )

        detectedChars = []
        classes = ocrResults[0].boxes.cls
        typeOfVehicle = int(classes[0])

        if len(classes) > 0:
            for ocrResult in ocrResults:
                boxes = ocrResult.boxes
                classIds = boxes.cls
                xyxy = boxes.xyxy

                for classId in range(len(classIds)):
                    className = self.model.names[int(classIds[classId])]
                    centerX = (xyxy[classId][0] + xyxy[classId][2]) / 2
                    centerY = (xyxy[classId][1] + xyxy[classId][3]) / 2

                    if classId >= 4:
                        detectedChars.append((className, centerX, centerY))

                upperRowText = []
                lowerRowText = []
                height = detectResults.height
                centerY = height / 2

                for char, x, y in detectedChars:
                    if y < centerY:
                        upperRowText.append((char, x))
                    else:
                        lowerRowText.append((char, x))

                typeOfVehicle = self.model.names[typeOfVehicle]
                upperRowText.sort(key=lambda item: item[1])
                lowerRowText.sort(key=lambda item: item[1])
                upperRowText = [char for char, _ in upperRowText]
                lowerRowText = [char for char, _ in lowerRowText]

        return typeOfVehicle, upperRowText, lowerRowText
