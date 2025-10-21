__package__ = "TEST_OCR"

from ultralytics import YOLO
import cv2
import os
import TRAIN
import re
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class TEST_OCR:
    MODEL_TO_LOAD_DETECT = None
    MODEL_TO_LOAD_OCR = None
    LAST_PT_PATH_DETECT = None
    LAST_PT_PATH_OCR = None
    TEST_DIR = "./test_ocr"
    OUTPUT_DETECT_DIR = f"{TRAIN.TRAIN.OUTPUT_DIR}_detect"
    OUTPUT_OCR_DIR = f"{TRAIN.TRAIN.OUTPUT_DIR}_ocr"
    MODEL_NAME = "yolo11n"
    MODEL_DETECT = None
    MODEL_OCR = None
    NAME_DETECT = "license_plate_11n_detect"
    NAME_OCR = "license_plate_11n_ocr"

    FONT_PATH = "./fonts/HiraginoMaruGothicProNW4.otf"

    def __init__(self, confNumber):
        confNumber = float(confNumber) / 100.0
        
        def extract_plate_parts(text):
            officeCode = ""
            classNumber = ""
            hiragana = ""
            registrationNumber = ""
            
            if not text:
                return "", "", "", ""

            matchedIndex = 0
            for i, char in enumerate(text):
                if char.isdigit():
                    officeCode = text[:i]
                    matchedIndex = i
                    break
                elif i >= len(text) - 1:
                    return text, "", "", ""
            
            if not officeCode:
                return text, "", "", ""

            remainder = text[matchedIndex:]
            
            if len(remainder) >= 2 and remainder[0].isdigit() and remainder[1].isdigit():
                
                if len(remainder) >= 3 and remainder[2].isdigit():
                    if len(remainder) >= 4 and not remainder[3].isdigit():
                        classNumber = remainder[:3]
                        hiragana = remainder[3]
                        registrationNumber = remainder[4:]
                    else:
                        classNumber = remainder[:3] 
                        registrationNumber = remainder[3:]
                
                elif len(remainder) >= 3 and not remainder[2].isdigit():
                    classNumber = remainder[:2]
                    hiragana = remainder[2]
                    registrationNumber = remainder[3:]
                    
                else:
                    return officeCode, remainder, "", ""
            
            if len(registrationNumber) == 4:
                registrationNumber = f"{registrationNumber[:2]}-{registrationNumber[2:]}"

            return officeCode, classNumber, hiragana, registrationNumber
        
        try:
            if os.path.exists(self.OUTPUT_DETECT_DIR):
                folderNames = os.listdir(self.OUTPUT_DETECT_DIR)
                pattern = re.compile(rf'^({self.NAME_DETECT})(\d+)$')
                numbered_folders = []
                for name in folderNames:
                    match = pattern.match(name)
                    if match:
                        number = int(match.group(2))
                        numbered_folders.append((number, name))
                if numbered_folders:
                    latest_folder_name = max(numbered_folders)[1] 
                    self.LAST_PT_PATH_DETECT = os.path.join(
                        self.OUTPUT_DETECT_DIR,
                        latest_folder_name,
                        "weights",
                        "best.pt"
                    )
                    if os.path.exists(self.LAST_PT_PATH_DETECT):
                        self.MODEL_TO_LOAD_DETECT = self.LAST_PT_PATH_DETECT
                if self.MODEL_TO_LOAD_DETECT:
                    self.MODEL_DETECT = YOLO(self.MODEL_TO_LOAD_DETECT)
                    print(f"前回の学習結果（{self.MODEL_TO_LOAD_DETECT}）を読み込みました。")
                elif os.path.exists(os.path.join(self.OUTPUT_DETECT_DIR, self.NAME_DETECT, "weights", "best.pt")):
                    self.MODEL_DETECT = YOLO(os.path.join(self.OUTPUT_DETECT_DIR, self.NAME_DETECT, "weights", "best.pt"))
                    print(f"前回の学習結果({self.NAME_DETECT}/weights/best.pt)を読み込みました。")
                else:
                    print("ERROR: 位置検知モデルの学習結果がありません。学習を行ってください。")
                    return
            else:
                print("ERROR: 位置検知モデルの学習結果がありません。学習を行ってください。")
                return
        except OSError:
            raise RuntimeError("ERROR: 位置検知モデルの読み込みに失敗しました。")
        except FileNotFoundError:
            raise RuntimeError("ERROR: 位置検知モデルが見つかりません。")

        try:
            if os.path.exists(self.OUTPUT_OCR_DIR):
                folderNames = os.listdir(self.OUTPUT_OCR_DIR)
                pattern = re.compile(rf'^({self.NAME_OCR})(\d+)$')
                numbered_folders = []
                for name in folderNames:
                    match = pattern.match(name)
                    if match:
                        number = int(match.group(2))
                        numbered_folders.append((number, name))
                if numbered_folders:
                    latest_folder_name = max(numbered_folders)[1] 
                    self.LAST_PT_PATH_OCR = os.path.join(
                        self.OUTPUT_OCR_DIR,
                        latest_folder_name,
                        "weights",
                        "best.pt"
                    )
                    if os.path.exists(self.LAST_PT_PATH_OCR):
                        self.MODEL_TO_LOAD_OCR = self.LAST_PT_PATH_OCR
                if self.MODEL_TO_LOAD_OCR:
                    self.MODEL_OCR = YOLO(self.MODEL_TO_LOAD_OCR)
                    print(f"前回の学習結果（{self.MODEL_TO_LOAD_OCR}）を読み込みました。")
                elif os.path.exists(os.path.join(self.OUTPUT_OCR_DIR, self.NAME_OCR, "weights", "best.pt")):
                    self.MODEL_OCR = YOLO(os.path.join(self.OUTPUT_OCR_DIR, self.NAME_OCR, "weights", "best.pt"))
                    print(f"前回の学習結果({self.NAME_OCR}/weights/best.pt)を読み込みました。")
                else:
                    print("ERROR: OCRモデルの学習結果がありません。学習を行ってください。")
                    return
            else:
                print("ERROR: OCRモデルの学習結果がありません。学習を行ってください。")
                return
        except OSError:
            raise RuntimeError("ERROR: OCRモデルの読み込みに失敗しました。")
        except FileNotFoundError:
            raise RuntimeError("ERROR: OCRモデルが見つかりません。")

        try:
            if not os.path.exists(self.TEST_DIR):
                print("ERROR: テスト画像を追加してください。")
                os.makedirs(self.TEST_DIR + "/test_images")
                return
            if not os.path.exists(self.TEST_DIR + "/test_images"):
                print("ERROR: テスト画像を追加してください。")
                os.makedirs(self.TEST_DIR + "/test_images")
                return
            if os.listdir(self.TEST_DIR + "/test_images") == []:
                print("ERROR: テスト画像を追加してください。")
                return
            if not os.path.exists(self.TEST_DIR + "/results_images"):
                os.makedirs(self.TEST_DIR + "/results_images")
            else:
                for file in os.listdir(self.TEST_DIR + "/results_images"):
                    os.remove(os.path.join(self.TEST_DIR + "/results_images", file))

            font = ImageFont.truetype(self.FONT_PATH, 32)

            for file in os.listdir(self.TEST_DIR + "/test_images"):
                image = cv2.imread(os.path.join(self.TEST_DIR, "test_images", file))
                detectResult = self.MODEL_DETECT(image, conf=confNumber, save=False)
                detections = detectResult[0].boxes.xyxy
                licensePlateNumber = len(detections)

                image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                draw = ImageDraw.Draw(image_pil)
                draw.text((10, 10), f"Number of License Plates: {licensePlateNumber}", font=font, fill=(0, 255, 0))

                for r in detections:
                    x1, y1, x2, y2 = map(int, r[:4])
                    
                    draw.rectangle([(x1, y1), (x2, y2)], outline=(0, 255, 0), width=3)
                    
                    plateImage = image[y1:y2, x1:x2]
                    
                    ocrResult = self.MODEL_OCR(plateImage, conf=confNumber, save=False)

                    detectedChars = []
                    for ocrR in ocrResult:
                        boxes = ocrR.boxes
                        classIds = boxes.cls
                        xyxy = boxes.xyxy
                        for i in range(len(classIds)):
                            classId = int(classIds[i])
                            className = self.MODEL_OCR.names[classId]
                            centerX = (int(xyxy[i][0]) + int(xyxy[i][2])) / 2
                            centerY = (int(xyxy[i][1]) + int(xyxy[i][3])) / 2
                            
                            detectedChars.append((centerX, className, centerY)) 

                    upperRow = []
                    lowerRow = []

                    plateImageHeight = y2 - y1
                    plateImageCenterY = plateImageHeight / 2
                    
                    for centerX, className, centerY in detectedChars:
                        if centerY < plateImageCenterY:
                            upperRow.append((centerX, className))
                        else:
                            lowerRow.append((centerX, className))

                    upperRow.sort(key=lambda x: x[0])
                    lowerRow.sort(key=lambda x: x[0])
                    
                    plateTextUpper = "".join([c[1] for c in upperRow])
                    plateTextLower = "".join([c[1] for c in lowerRow])
                    plateText = plateTextUpper + plateTextLower
                    
                    city, type_num, kana, reg_num = extract_plate_parts(plateText)
                    
                    if city:
                        formattedText = f"{city} {type_num} {kana} {reg_num}"
                        formattedText = formattedText.strip()
                        formattedText = ' '.join(formattedText.split())
                    else:
                        formattedText = plateText

                    draw.text((x1, y1 - 30), formattedText, font=font, fill=(0, 255, 255)) 

                image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
                cv2.imwrite(os.path.join(self.TEST_DIR + "/results_images", "result_" + file), image)

        except OSError:
            raise RuntimeError("ERROR: テスト画像の読み込みに失敗しました。")