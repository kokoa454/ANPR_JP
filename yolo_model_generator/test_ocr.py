import os
import re
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO
from data_set_ocr import DATA_SET_OCR
from train import TRAIN

# -- OCR用テストクラス --
class TEST_OCR:
    MODEL_TO_LOAD_DETECT = None
    MODEL_TO_LOAD_OCR = None
    LAST_PT_PATH_DETECT = None
    LAST_PT_PATH_OCR = None
    TEST_DIR = "./test_ocr"
    OUTPUT_DETECT_DIR = f"{TRAIN.OUTPUT_DIR}_detect"
    OUTPUT_OCR_DIR = f"{TRAIN.OUTPUT_DIR}_ocr"
    MODEL_NAME = "yolo26m"
    MODEL_DETECT = None
    MODEL_OCR = None
    NAME_DETECT = "number_plate_26m_detect"
    NAME_OCR = "number_plate_26m_ocr"
    FONT_PATH = "./fonts/HiraginoMaruGothicProNW4.otf"

    def __init__(self, confNumberForDetect, confNumberForOCR, imgsz):
        confNumberForDetect = float(confNumberForDetect) / 100.0
        confNumberForOCR = float(confNumberForOCR) / 100.0
        
        self.loadModel()
        self.runTest(confNumberForDetect, confNumberForOCR, imgsz)
        
    def loadModel(self):
        try:
            if os.path.exists(self.OUTPUT_DETECT_DIR):
                folderNames = os.listdir(self.OUTPUT_DETECT_DIR)
                pattern = re.compile(rf'^({self.NAME_DETECT})(\d+)$')
                numberedFolders = []
                for name in folderNames:
                    match = pattern.match(name)
                    if match:
                        number = int(match.group(2))
                        numberedFolders.append((number, name))
                if numberedFolders:
                    latestFolderName = max(numberedFolders)[1] 
                    self.LAST_PT_PATH_DETECT = os.path.join(
                        self.OUTPUT_DETECT_DIR,
                        latestFolderName,
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
                numberedFolders = []
                for name in folderNames:
                    match = pattern.match(name)
                    if match:
                        number = int(match.group(2))
                        numberedFolders.append((number, name))
                if numberedFolders:
                    latestFolderName = max(numberedFolders)[1] 
                    self.LAST_PT_PATH_OCR = os.path.join(
                        self.OUTPUT_OCR_DIR,
                        latestFolderName,
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

    def runTest(self, confNumberForDetect, confNumberForOCR, imgsz):
        try:
            testImagesDir = os.path.join(self.TEST_DIR, "test_images")
            resultImagesDir = os.path.join(self.TEST_DIR, "results_images")

            if not os.path.exists(testImagesDir):
                os.makedirs(testImagesDir)
                print("ERROR: テスト画像を追加してください。")
                return
            if not os.listdir(testImagesDir):
                print("ERROR: テスト画像を追加してください。")
                return
            if not os.path.exists(resultImagesDir):
                os.makedirs(resultImagesDir)
            else:
                for f in os.listdir(resultImagesDir):
                    os.remove(os.path.join(resultImagesDir, f))

            font = ImageFont.truetype(self.FONT_PATH, 24) 

            # 推論実行開始
            for file in os.listdir(testImagesDir):
                image = cv2.imread(os.path.join(testImagesDir, file))

                if image.shape[0] < imgsz * 1.5:
                    newHeight = int(imgsz * 1.5)
                    newWidth = int(image.shape[1] * (newHeight / image.shape[0]))
                    image = cv2.resize(image, (newWidth, newHeight), interpolation=cv2.INTER_CUBIC)
                if image.shape[1] < imgsz * 1.5:
                    newWidth = int(imgsz * 1.5)
                    newHeight = int(image.shape[0] * (newWidth / image.shape[1]))
                    image = cv2.resize(image, (newWidth, newHeight), interpolation=cv2.INTER_CUBIC)
                
                overlay = image.copy()
                
                # 位置検知推論
                detectResult = self.MODEL_DETECT(
                    image, 
                    conf=confNumberForDetect, 
                    imgsz=imgsz, 
                    iou=0.5,
                    save=False
                )
                detections = detectResult[0].boxes.xyxy
                masks = detectResult[0].masks
                numberPlateNumber = len(detections)

                # 推論結果の描画
                if masks is not None:
                    segmentMasks = masks.data.cpu().numpy()
                    n = min(len(segmentMasks), len(detections))

                    for i in range(n):
                        mask = segmentMasks[i]
                        resizedMask = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
                        maskBoolean = resizedMask > 0.5
                        overlay[maskBoolean] = (0, 255, 0) # マスク描画
                        
                        x1, y1, x2, y2 = map(int, detections[i])
                        cv2.rectangle(overlay, (x1, y1), (x2, y2), (255, 0, 0), 2) # バウンディングボックス描画

                        # OCR処理用の変形
                        mask8bit = (maskBoolean * 255).astype(np.uint8)
                        mask8bit = cv2.morphologyEx(cv2.medianBlur(mask8bit, 7), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
                        contours, _ = cv2.findContours(mask8bit, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                        resizedMask = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
                        maskBoolean = resizedMask > 0.5
                        mask8bit = (maskBoolean * 255).astype(np.uint8)
                        mask8bit = cv2.medianBlur(mask8bit, 7)
                        kernel = np.ones((7, 7), np.uint8)
                        mask8bit = cv2.morphologyEx(mask8bit, cv2.MORPH_CLOSE, kernel)

                        # 凸包判定
                        contours, _ = cv2.findContours(mask8bit, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        sourcePoints = None
                        
                        if contours:
                            mainHull = max(contours, key=cv2.contourArea)
                            approx = cv2.approxPolyDP(mainHull, 0.02 * cv2.arcLength(mainHull, True), True)
                            sourcePoints = self.sortPoints(np.float32(approx.reshape(-1, 2)) if len(approx) == 4 else cv2.boxPoints(cv2.minAreaRect(mainHull)))
                            plateImage = self.perspectiveTransform(image, sourcePoints)

                            if contours:
                                mainHull = max(contours, key=cv2.contourArea)
                                perimeter = cv2.arcLength(mainHull, True)
                                epsilon = 0.02 * perimeter                            
                                approx = cv2.approxPolyDP(mainHull, epsilon, True)
                                
                                if approx.shape[0] == 4:
                                    sourcePoints = np.float32(approx.reshape(4, 2))
                                    sourcePoints = self.sortPoints(sourcePoints)
                                else:
                                    rectangle = cv2.minAreaRect(mainHull)
                                    box = cv2.boxPoints(rectangle)
                                    sourcePoints = np.float32(box)
                                    sourcePoints = self.sortPoints(sourcePoints)

                            # 射影変換
                            if sourcePoints is not None:
                                plateImage = self.perspectiveTransform(image, sourcePoints)
                            else:
                                print(f"Skipping detection {i}: Could not find source points.")
                                continue
                            
                            # アンシャープマスキング
                            gaussian = cv2.GaussianBlur(plateImage, (0, 0), 2)
                            plateImage = cv2.addWeighted(plateImage, 1.5, gaussian, -0.5, 0)

                            # バイラテラルフィルタ
                            plateImage = cv2.bilateralFilter(plateImage, d=9, sigmaColor=75, sigmaSpace=75)

                            # ディテールエンハンス
                            plateImage = cv2.detailEnhance(plateImage, sigma_s=10, sigma_r=0.15)

                            # ノイズ除去
                            plateImage = cv2.fastNlMeansDenoisingColored(plateImage, None, h=10, hColor=10, templateWindowSize=7, searchWindowSize=21)

                            cv2.imwrite(f"{resultImagesDir}/result_perspective{i + 1}_{file}", plateImage)

                            ocrResult = self.MODEL_OCR(
                                plateImage, 
                                conf=confNumberForOCR, 
                                imgsz=imgsz, 
                                save=False
                            )

                            detectedChars = []

                            for ocrR in ocrResult:
                                boxes = ocrR.boxes
                                classIds = boxes.cls
                                xyxy = boxes.xyxy
                                
                                for j in range(len(classIds)):
                                    classId = int(classIds[j])
                                    className = self.MODEL_OCR.names[classId]
                                    centerX = (xyxy[j][0] + xyxy[j][2]) / 2
                                    centerY = (xyxy[j][1] + xyxy[j][3]) / 2

                                    if classId >= 4: 
                                        detectedChars.append((centerX, className, centerY))

                            # 文字列整形
                            upperRowChars, lowerRowChars = [], []
                            h = plateImage.shape[0]
                            centerY = h / 2

                            for cx, ch, cy in detectedChars:
                                (upperRowChars if cy < centerY else lowerRowChars).append((cx, ch))

                            upperRowChars.sort(key=lambda x: x[0])
                            lowerRowChars.sort(key=lambda x: x[0])

                            upperRow = "".join([c[1] for c in upperRowChars])
                            lowerRow = "".join([c[1] for c in lowerRowChars])
                                
                            plateText = self.formatNumberPlateText(upperRow, lowerRow)
                            
                            pilOverlay = Image.fromarray(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
                            draw = ImageDraw.Draw(pilOverlay)
                            self.drawMultilineText(draw, (x1, y1 - 150), plateText, font, (255, 0, 0), 45)
                            overlay = cv2.cvtColor(np.array(pilOverlay), cv2.COLOR_RGB2BGR)

                # 最終合成
                finalImage = cv2.addWeighted(overlay, 0.7, image, 0.3, 0)
                
                cv2.putText(finalImage, f"Number of Number Plates: {numberPlateNumber}", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)
                
                cv2.imwrite(os.path.join(resultImagesDir, "result_" + file), finalImage)

        except Exception as e:
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"テスト実行エラー: {e}")

    def sortPoints(self, points):
        points = sorted(points, key=lambda x: (x[1], x[0]))
        top = sorted(points[:2], key=lambda x: x[0])
        bottom = sorted(points[2:], key=lambda x: x[0], reverse=True)
        return np.array([top[0], top[1], bottom[0], bottom[1]], dtype="float32")

    def perspectiveTransform(self, image, sourcePoints):
        TARGET_WIDTH = 440 * 2
        TARGET_HEIGHT = 220 * 2

        destination = np.array([
            [0, 0], 
            [TARGET_WIDTH - 1, 0],
            [TARGET_WIDTH - 1, TARGET_HEIGHT - 1],
            [0, TARGET_HEIGHT - 1]
        ], dtype="float32")

        homographyMatrix, _ = cv2.findHomography(sourcePoints, destination, cv2.RANSAC, 5.0)
        
        warpedPerspective = cv2.warpPerspective(
            image, 
            homographyMatrix, 
            (TARGET_WIDTH, TARGET_HEIGHT),
            flags=cv2.INTER_CUBIC
        )
        
        finalImage = warpedPerspective
            
        return finalImage

    def formatNumberPlateText(self, upperRow, lowerRow):
        officeCode = ""
        classNum = ""
        hiraganaCode = ""
        regiNum = ""

        for char in upperRow:
            if char.isdigit() or char in DATA_SET_OCR.ALPHABET_LIST:
                classNum += char
            else:
                officeCode += char

        for char in lowerRow:
            if char.isdigit() or char in DATA_SET_OCR.SPECIAL_CHARACTER_LIST:
                regiNum += char
            else:
                hiraganaCode += char

        if officeCode == "" or officeCode not in DATA_SET_OCR.PLACE_CODE_LIST:
            officeCode = "??"

        if classNum == "" or len(classNum) < 2 or len(classNum) > 4:
            classNum = "???"

        if hiraganaCode == "" or hiraganaCode not in DATA_SET_OCR.HIRAGANA_LIST_ALL:
            hiraganaCode = "?"

        if regiNum == "" or (len(regiNum) != 4 and len(regiNum) != 5) or re.match(r'・\d{3}|・{2}\d{2}|・{3}\d{1}|\d{2}-\d{2}$', regiNum) is None:
            regiNum = "????"

        return f"{officeCode} {classNum} {hiraganaCode} {regiNum}"

    def drawMultilineText(self, draw, position, text, font, fill, fontSize):
        x, y = position
        font = ImageFont.truetype(self.FONT_PATH, fontSize)
        try:
            bbox = font.getbbox("AA") 
            lineHeight = bbox[3] - bbox[1]
        except Exception:
            lineHeight = font.size * 1.5 
            
        for line in text.split('\n'):
            draw.text((x, y), line, font=font, fill=fill)
            y += lineHeight
