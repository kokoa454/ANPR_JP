__package__ = "DATA_SET_OCR"

import random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
import numpy as np
import shutil

class DATA_SET_OCR:
    DATA_SET_OCR_DIR = "./data_set_ocr"
    YOLO_DATA_YAML_PATH = DATA_SET_OCR_DIR + "/data.yaml"
    
    TYPE_OF_VEHICLE_STRING = ["普通_自家用", "普通_事業用", "軽_自家用", "軽_事業用"]
    TYPE_OF_VEHICLE_ROMAN = {
        "普通_自家用": "F_JIKAYO",
        "普通_事業用": "F_JIGYOYO",
        "軽_自家用": "K_JIKAYO",
        "軽_事業用": "K_JIGYOYO"
    }

    LICENSE_PLATE_WIDTH = 440
    LICENSE_PLATE_HEIGHT = 220
    
    ALPHABET_LIST = ["A", "C", "F", "H", "K", "L", "M", "P", "X", "Y"]
    ALPHABET_CLASS_ID_LIST = []
    
    OFFICE_CODE_LIST = [
        "札幌","函館","旭川","室蘭","苫小牧","釧路","知床","帯広","十勝","北見",
        "青森","弘前","八戸",
        "盛岡","平泉", "岩手",
        "宮城","仙台",
        "秋田",
        "山形","庄内",
        "福島","会津","郡山","白河","いわき",
        "水戸","土浦","つくば",
        "宇都宮","那須","とちぎ", "日光",
        "前橋","高崎","群馬",
        "大宮","川口","春日部","熊谷","所沢","越谷","川越",
        "千葉","習志野","成田","柏","袖ヶ浦","野田",
        "板橋","練馬","足立","江東","品川","多摩","八王子", "江戸川", "世田谷", "杉並", "葛飾",
        "横浜","川崎","相模","湘南","平塚","厚木",
        "山梨","富士山",
        "新潟","長岡","上越","長野","松本","諏訪","諏訪湖","南信州","安曇野",
        "富山","石川","金沢",
        "福井",
        "岐阜","飛騨",
        "静岡","浜松","沼津","伊豆",
        "名古屋","三河","岡崎","豊田","尾張小牧","一宮","知多",
        "三重","鈴鹿","伊勢志摩", "四日市",
        "滋賀","彦根",
        "京都","舞鶴",
        "大阪","なにわ","和泉","堺","富田林",
        "奈良",
        "和歌山",
        "神戸","姫路","西宮","伊丹",
        "鳥取","倉吉",
        "島根","出雲",
        "岡山","倉敷","備前",
        "広島","福山","呉","尾道",
        "山口","下関","周南","岩国","宇部",
        "徳島",
        "香川","高松",
        "愛媛","松山","今治","宇和島",
        "高知","土佐",
        "福岡","北九州","久留米","筑豊",
        "佐賀",
        "長崎","佐世保",
        "熊本","阿蘇",
        "大分","別府",
        "宮崎",
        "鹿児島","奄美",
        "沖縄"
    ]

    HIRAGANA_LIST_F_JIKAYO = ["さ", "す", "せ", "そ", "た", "ち", "つ", "て", "と", "な", "に", "ぬ", "ね", "の", "は", "ひ", "ふ", "ほ", "ま", "み", "む", "め", "も", "や", "ゆ", "ら", "り", "る", "ろ"]
    HIRAGANA_LIST_F_JIGYOYO = ["あ", "い", "う", "え", "か", "き", "く", "け", "こ", "れ", "わ"]
    HIRAGANA_LIST_K_JIKAYO = ["あ", "い", "う", "え", "か", "き", "く", "け", "こ", "さ", "す", "せ", "そ", "た", "ち", "つ", "て", "と", "な", "に", "ぬ", "ね", "の", "は", "ひ", "ふ", "ほ", "ま", "み", "む", "め", "も", "や", "ゆ", "よ", "ら", "る", "ろ"]
    HIRAGANA_LIST_K_JIGYOYO = ["り", "れ", "わ"]

    HIRAGANA_LIST_ALL = [
        "あ", "い", "う", "え",
        "か", "き", "く", "け", "こ",
        "さ", "す", "せ", "そ",
        "た", "ち", "つ", "て", "と",
        "な", "に", "ぬ", "ね", "の",
        "は", "ひ", "ふ", "へ", "ほ",
        "ま", "み", "む", "め", "も",
        "や", "ゆ", "よ",
        "ら", "り", "る", "れ", "ろ",
        "わ",
    ]

    SPECIAL_CHARACTER_LIST = ["・", "-"]

    CHARACTER_NAMES = []
    CHARACTER_NAMES.extend(OFFICE_CODE_LIST)
    CHARACTER_NAMES.extend([str(i) for i in range(10)])
    CHARACTER_NAMES.extend(HIRAGANA_LIST_ALL)
    CHARACTER_NAMES.extend(ALPHABET_LIST)
    CHARACTER_NAMES.extend(SPECIAL_CHARACTER_LIST)

    NAME_TO_ID = {name: i for i, name in enumerate(CHARACTER_NAMES)}
    
    def __init__(self, trainingNumber):
        trainNumber = int(trainingNumber * 0.8)
        validationNumber = trainingNumber - trainNumber
        
        if os.path.exists(DATA_SET_OCR.DATA_SET_OCR_DIR):
            print("\n前回のOCR用データセットを削除します。")
            shutil.rmtree(DATA_SET_OCR.DATA_SET_OCR_DIR)
            print("前回のOCR用データセットを削除しました。")
        
        os.makedirs(DATA_SET_OCR.DATA_SET_OCR_DIR + "/train/images", exist_ok=True)
        os.makedirs(DATA_SET_OCR.DATA_SET_OCR_DIR + "/train/labels", exist_ok=True)
        os.makedirs(DATA_SET_OCR.DATA_SET_OCR_DIR + "/valid/images", exist_ok=True)
        os.makedirs(DATA_SET_OCR.DATA_SET_OCR_DIR + "/valid/labels", exist_ok=True)
        
        print("\nOCR用データセット生成中...")

        VehicleTypesNumber = len(self.TYPE_OF_VEHICLE_STRING)
        fileNameLength = len(str(trainingNumber)) + 1

        for typeOfVehicle in range(VehicleTypesNumber):
            currentImageCount = 0
            for imageNumber in range(1, trainNumber + 1):
                plateBackGroundColor = self.getPlateBackGroundColor(typeOfVehicle)
                plateTextColor = self.getPlateTextColor(typeOfVehicle)
                officeCode = self.getOfficeCode()
                classNumber = self.getClassNumber(typeOfVehicle)
                hiraganaCode = self.getHiraganaCode(typeOfVehicle)
                registrationNumber = self.getRegistrationNumber()

                fileName = f"train_{self.TYPE_OF_VEHICLE_ROMAN[self.TYPE_OF_VEHICLE_STRING[typeOfVehicle]]}_{imageNumber:0{fileNameLength}}" 
                self.generatePlate(fileName, "train", plateBackGroundColor, plateTextColor, officeCode, classNumber, hiraganaCode, registrationNumber)

                currentImageCount += 1
                progress = int(currentImageCount / trainNumber * 50)
                bar = "█" * progress + "-" * (50 - progress)
                print(f"\r[{bar}] {currentImageCount}/{trainNumber} | {self.TYPE_OF_VEHICLE_STRING[typeOfVehicle]} | train", end="", flush=True)
            
            print("\n")

            currentImageCount = 0
            for imageNumber in range(1, validationNumber + 1):
                plateBackGroundColor = self.getPlateBackGroundColor(typeOfVehicle)
                plateTextColor = self.getPlateTextColor(typeOfVehicle)
                officeCode = self.getOfficeCode()
                classNumber = self.getClassNumber(typeOfVehicle)
                hiraganaCode = self.getHiraganaCode(typeOfVehicle)
                registrationNumber = self.getRegistrationNumber()

                fileName = f"valid_{self.TYPE_OF_VEHICLE_ROMAN[self.TYPE_OF_VEHICLE_STRING[typeOfVehicle]]}_{imageNumber:0{fileNameLength}}" 
                self.generatePlate(fileName, "valid", plateBackGroundColor, plateTextColor, officeCode, classNumber, hiraganaCode, registrationNumber)

                currentImageCount += 1
                progress = int(currentImageCount / validationNumber * 50)
                bar = "█" * progress + "-" * (50 - progress)
                print(f"\r[{bar}] {currentImageCount}/{validationNumber} | {self.TYPE_OF_VEHICLE_STRING[typeOfVehicle]} | valid", end="", flush=True)
            
            print("\n\n")

        print("\nYOLO用data.yamlファイルを作成中...")
        self.createYamlFile()
        print("YOLO用data.yamlファイル作成完了")

        print("\nOCR用データセット生成完了")
    
    def createYamlFile(self):
        yamlContent = f"""
# YOLO11 data.yaml
train: ../train/images
val: ../valid/images
nc: {len(DATA_SET_OCR.CHARACTER_NAMES)}
names: {DATA_SET_OCR.CHARACTER_NAMES}
"""
        with open(DATA_SET_OCR.YOLO_DATA_YAML_PATH, 'w', encoding='utf-8') as f:
            f.write(yamlContent.strip())
        print(f"data.yamlを {DATA_SET_OCR.YOLO_DATA_YAML_PATH} に作成しました。")
        
    def getPlateBackGroundColor(self, typeOfVehicle):
        colorList = [
            ("white", (240, 240, 240)),
            ("green", (0, 60, 0)),
            ("yellow", (255, 255, 0)),
            ("black", (0, 0, 0))
        ]
        return colorList[typeOfVehicle]

    def getPlateTextColor(self, typeOfVehicle):
        colorList = [
            ("green", (0, 60, 0)),
            ("white", (240, 240, 240)),
            ("black", (0, 0, 0)),
            ("yellow", (255, 255, 0))
        ]
        return colorList[typeOfVehicle]
    
    def getOfficeCode(self):
        return random.choice(DATA_SET_OCR.OFFICE_CODE_LIST)

    def getClassNumber(self, typeOfVehicle):
        alphabetList = DATA_SET_OCR.ALPHABET_LIST
        
        if typeOfVehicle in (0, 1):
            classNumber = str(random.choice([1, 2, 3, 8, 9, 0]))
            
            randomNum = random.randint(0, 1)

            if randomNum == 0:
                classNumber += str(random.randint(0, 9))

            else:
                randomNum = random.randint(0, 2)
                
                if randomNum == 0:
                    classNumber += str(random.randint(0, 9))
                    classNumber += str(random.randint(0, 9))

                elif randomNum == 1:
                    classNumber += str(random.randint(0, 9))
                    classNumber += random.choice(alphabetList)

                else:
                    classNumber += random.choice(alphabetList)
                    classNumber += random.choice(alphabetList)

        else:
            classNumber = str(random.choice([4, 5, 6, 7, 8]))
            randomNum = random.randint(0, 1)
            
            if randomNum == 0:
                classNumber += str(random.randint(0, 9))
            else:
                randomNum = random.randint(0, 2)
                if randomNum == 0:
                    classNumber += str(random.randint(0, 9))
                    classNumber += str(random.randint(0, 9))
                elif randomNum == 1:
                    classNumber += str(random.randint(0, 9))
                    classNumber += random.choice(alphabetList)
                else:
                    classNumber += random.choice(alphabetList)
                    classNumber += random.choice(alphabetList)

        return classNumber

    def getHiraganaCode(self, typeOfVehicle):
        if typeOfVehicle == 0:
            hiraganaList = DATA_SET_OCR.HIRAGANA_LIST_F_JIKAYO
        elif typeOfVehicle == 1:
            hiraganaList = DATA_SET_OCR.HIRAGANA_LIST_F_JIGYOYO
        elif typeOfVehicle == 2:
            hiraganaList = DATA_SET_OCR.HIRAGANA_LIST_K_JIKAYO
        else:
            hiraganaList = DATA_SET_OCR.HIRAGANA_LIST_K_JIGYOYO
            
        return random.choice(hiraganaList)

    def getRegistrationNumber(self):
        prefixRegistrationNumber = random.randint(1, 99)
        
        if prefixRegistrationNumber < 10:
            registrationNumber = "・" + str(prefixRegistrationNumber)
        else:
            registrationNumber = str(prefixRegistrationNumber)

        registrationNumber += "-"
        registrationNumber += f"{random.randint(0, 99):02d}"

        return registrationNumber

    def get_yolo_bbox_from_absolute(self, xmin, ymin, xmax, ymax, width, height):
        x_center = ((xmin + xmax) / 2) / width
        y_center = ((ymin + ymax) / 2) / height
        w = (xmax - xmin) / width
        h = (ymax - ymin) / height
        return x_center, y_center, w, h

    def generatePlate(self, fileName, trainOrValid, plateBackgroundColor, plateTextColor, officeCode, classNumber, hiraganaCode, registrationNumber):
        HEIGHT = self.LICENSE_PLATE_HEIGHT
        WIDTH = self.LICENSE_PLATE_WIDTH

        FONT_HIRAGINO = "./fonts/HiraginoMaruGothicProNW4.otf"
        FONT_TRM = "./fonts/TrmFontJB.ttf"
        FONT_FZ = "./fonts/FZcarnumberJA-OTF_ver10.otf"

        MARGIN = 4
        RADIUS = 6
        COLOR_FOR_FRAME = (128, 128, 128)
        
        FONT_SIZE_OFFICE = 55
        THICKNESS_OFFICE = 1.2
        FONT_SIZE_CLASS = 58
        THICKNESS_CLASS = 1.2
        
        img = Image.new("RGB", (WIDTH, HEIGHT), plateBackgroundColor[1])
        draw = ImageDraw.Draw(img)

        draw.rectangle([(0, 0), (WIDTH - 1, HEIGHT - 1)], outline = COLOR_FOR_FRAME, width = MARGIN)
        draw.ellipse([(80 - RADIUS, 30 - RADIUS), (80 + RADIUS, 30 + RADIUS)], fill = COLOR_FOR_FRAME)
        draw.ellipse([(360 - RADIUS, 30 - RADIUS), (360 + RADIUS, 30 + RADIUS)], fill = COLOR_FOR_FRAME)

        for font in [FONT_HIRAGINO, FONT_TRM, FONT_FZ]:
            if not os.path.exists(font):
                raise FileNotFoundError(f"ERROR: フォントファイル '{font}' が見つかりません。")

        yoloLabels = []
        dummyImg = Image.new("RGB", (1, 1))
        dummyDraw = ImageDraw.Draw(dummyImg)

        # 1. 地名 (officeCode)
        fontOfficeCode = ImageFont.truetype(FONT_HIRAGINO, FONT_SIZE_OFFICE)
        positionForOfficeCode = [105, 10]
        
        if len(officeCode) < 2:
            positionForOfficeCode[0] = 120
            draw.text(positionForOfficeCode, officeCode, font=fontOfficeCode, stroke_width=int(THICKNESS_OFFICE), fill=plateTextColor[1])
            bboxOffice = draw.textbbox(positionForOfficeCode, officeCode, font=fontOfficeCode, stroke_width=int(THICKNESS_OFFICE))
        
        elif len(officeCode) <= 2:
            positionForOfficeCode[0] = 105
            draw.text(positionForOfficeCode, officeCode, font=fontOfficeCode, stroke_width=int(THICKNESS_OFFICE), fill=plateTextColor[1])
            bboxOffice = draw.textbbox(positionForOfficeCode, officeCode, font=fontOfficeCode, stroke_width=int(THICKNESS_OFFICE))
            
        else:
            compressRatio = 0.7 if len(officeCode) == 3 else 0.55
            positionForOfficeCode[0] = 105

            bbox = dummyDraw.textbbox((0, 0), officeCode, font=fontOfficeCode, stroke_width=int(THICKNESS_OFFICE))
            textWidth = bbox[2] - bbox[0]
            textHeight = bbox[3] - bbox[1]

            textImage = Image.new("RGBA", (textWidth, textHeight), (0, 0, 0, 0))
            textDraw = ImageDraw.Draw(textImage)
            textDraw.text((0, 0), officeCode, font=fontOfficeCode, stroke_width=int(THICKNESS_OFFICE), fill=plateTextColor[1])

            newWidth = int(textImage.width * compressRatio)
            resizedTextImage = textImage.resize((newWidth, textImage.height), Image.Resampling.LANCZOS)

            img.paste(resizedTextImage, positionForOfficeCode, resizedTextImage)
            
            bboxOffice = (positionForOfficeCode[0], positionForOfficeCode[1], positionForOfficeCode[0] + newWidth, positionForOfficeCode[1] + textImage.height)

        # 地名全体のYOLOラベル
        officeCodeClassId = self.NAME_TO_ID[officeCode]
        officeCodeXCenter, officeCodeYCenter, officeCodeW, officeCodeH = self.get_yolo_bbox_from_absolute(
            bboxOffice[0], bboxOffice[1], bboxOffice[2], bboxOffice[3], WIDTH, HEIGHT
        )
        yoloLabels.append(f"{officeCodeClassId} {officeCodeXCenter:.6f} {officeCodeYCenter:.6f} {officeCodeW:.6f} {officeCodeH:.6f}")


        # 2. 分類番号 (classNumber)
        fontClassNumber = ImageFont.truetype(FONT_HIRAGINO, FONT_SIZE_CLASS)
        positionForClassNumber = [230, 10]
        CHAR_SPACING = 36 # 適切な文字間隔 (classCharWidth * 0.9 に近い値)

        if len(classNumber) == 2:
            positionForClassNumber[0] = 260
            
        hasSpecialChar = any(char in classNumber for char in ["M", "W", "H", "X"]) and len(classNumber) == 3
        
        currentX = positionForClassNumber[0]
        yPos = positionForClassNumber[1]

        for char in classNumber:
            charClassId = self.NAME_TO_ID[char]
            
            if hasSpecialChar and char in ["M", "W", "H", "X"]:
                bboxChar = dummyDraw.textbbox((0, 0), char, font=fontClassNumber, stroke_width=int(THICKNESS_CLASS))
                textWidth = bboxChar[2] - bboxChar[0]
                textHeight = bboxChar[3] - bboxChar[1]

                padding = 10
                textImage = Image.new("RGBA", (textWidth, textHeight + padding), (0, 0, 0, 0))
                textDraw = ImageDraw.Draw(textImage)
                textDraw.text((0, 0), char, font=fontClassNumber, stroke_width=int(THICKNESS_CLASS), fill=plateTextColor[1])

                compressRatio = 0.9
                newWidth = int(textImage.width * compressRatio)
                resizedTextImage = textImage.resize((newWidth, textImage.height), Image.Resampling.LANCZOS)
                
                img.paste(resizedTextImage, (int(currentX), yPos), resizedTextImage)
                
                xmin = int(currentX)
                ymin = yPos
                xmax = int(currentX) + newWidth
                ymax = yPos + textImage.height
            else:
                draw.text((currentX, yPos), char, font=fontClassNumber, stroke_width=int(THICKNESS_CLASS), fill=plateTextColor[1])
                bbox = draw.textbbox((currentX, yPos), char, font=fontClassNumber, stroke_width=int(THICKNESS_CLASS))
                xmin, ymin, xmax, ymax = bbox

            # 分類番号の各文字のYOLOラベル
            xCenter, yCenter, w, h = self.get_yolo_bbox_from_absolute(xmin, ymin, xmax, ymax, WIDTH, HEIGHT)
            yoloLabels.append(f"{charClassId} {xCenter:.6f} {yCenter:.6f} {w:.6f} {h:.6f}")
            
            currentX += CHAR_SPACING

        # 3. ひらがな (hiraganaCode)
        positionForHiraganaCode = [20, 110]
        fontSizeForHiraganaCode = 55
        fontHiraganaCode = ImageFont.truetype(FONT_FZ, fontSizeForHiraganaCode)

        if hiraganaCode in ["あ", "い", "う", "か", "き", "く", "け", "こ", "せ", "を"]:
            positionForHiraganaCode = [16, 55]
            fontSizeForHiraganaCode = 180
            fontHiraganaCode = ImageFont.truetype(FONT_TRM, fontSizeForHiraganaCode)

        draw.text(positionForHiraganaCode, hiraganaCode, font=fontHiraganaCode, fill=plateTextColor[1])

        # ひらがな (hiraganaCode) のYOLOラベル
        bboxHiragana = draw.textbbox(positionForHiraganaCode, hiraganaCode, font=fontHiraganaCode)
        hiraganaClassId = self.NAME_TO_ID[hiraganaCode]
        hiraganaXCenter, hiraganaYCenter, hiraganaW, hiraganaH = self.get_yolo_bbox_from_absolute(
            bboxHiragana[0], bboxHiragana[1], bboxHiragana[2], bboxHiragana[3], WIDTH, HEIGHT
        )
        yoloLabels.append(f"{hiraganaClassId} {hiraganaXCenter:.6f} {hiraganaYCenter:.6f} {hiraganaW:.6f} {hiraganaH:.6f}")


        # 4. 登録番号 (registrationNumber)
        fontSizeForRegistrationNumber = 130
        fontRegistrationNumber = ImageFont.truetype(FONT_TRM, fontSizeForRegistrationNumber)
        positionForRegistrationNumber = [80, 80]
        REG_CHAR_WIDTH = 60
        
        currentX = positionForRegistrationNumber[0]
        yPos = positionForRegistrationNumber[1]

        for char in registrationNumber:
            charClassId = self.NAME_TO_ID[char]
            
            xPos = currentX

            if char == '-':
                lineWidth = 10
                lineLength = 30
                centerX = xPos + REG_CHAR_WIDTH / 2
                centerY = yPos + fontSizeForRegistrationNumber / 2
                
                draw.line(
                    (centerX - lineLength/2, centerY, centerX + lineLength/2, centerY),
                    fill=plateTextColor[1], width=lineWidth
                )

                # ハイフン (-) のYOLOラベル
                xminHyphen = centerX - lineLength/2
                yminHyphen = centerY - lineWidth/2
                xmaxHyphen = centerX + lineLength/2
                ymaxHyphen = centerY + lineWidth/2
                
                xCenter, yCenter, w, h = self.get_yolo_bbox_from_absolute(
                    xminHyphen, yminHyphen, xmaxHyphen, ymaxHyphen, WIDTH, HEIGHT
                )
                yoloLabels.append(f"{charClassId} {xCenter:.6f} {yCenter:.6f} {w:.6f} {h:.6f}")
                currentX += REG_CHAR_WIDTH
                continue

            elif char == '・':
                dotRadius = 6
                dotCenterX = xPos + REG_CHAR_WIDTH / 2
                dotCenterY = yPos + fontSizeForRegistrationNumber * 0.4
                
                draw.ellipse(
                    [(dotCenterX - dotRadius, dotCenterY - dotRadius),
                    (dotCenterX + dotRadius, dotCenterY + dotRadius)],
                    fill=plateTextColor[1]
                )
                
                # ドット (・) のYOLOラベル
                xminDot = dotCenterX - dotRadius
                yminDot = dotCenterY - dotRadius
                xmaxDot = dotCenterX + dotRadius
                ymaxDot = dotCenterY + dotRadius
                
                xCenter, yCenter, w, h = self.get_yolo_bbox_from_absolute(
                    xminDot, yminDot, xmaxDot, ymaxDot, WIDTH, HEIGHT
                )
                yoloLabels.append(f"{charClassId} {xCenter:.6f} {yCenter:.6f} {w:.6f} {h:.6f}")
                currentX += REG_CHAR_WIDTH
                continue

            # 数字の描画
            draw.text((xPos, yPos), char, font=fontRegistrationNumber, fill=plateTextColor[1])
            
            # 数字のYOLOラベル
            bboxRegistrationChar = draw.textbbox((xPos, yPos), char, font=fontRegistrationNumber)
            
            xCenter, yCenter, w, h = self.get_yolo_bbox_from_absolute(
                bboxRegistrationChar[0], bboxRegistrationChar[1], bboxRegistrationChar[2], bboxRegistrationChar[3], WIDTH, HEIGHT
            )
            yoloLabels.append(f"{charClassId} {xCenter:.6f} {yCenter:.6f} {w:.6f} {h:.6f}")
            currentX += REG_CHAR_WIDTH

        # ノイズ付与
        levelOfGaussianNoise = random.randint(0, 30)
        img = self.makeGaussianNoise(img, levelOfGaussianNoise)

        levelOfPepperAndSaltNoise = random.randint(0, 5)
        img = self.makePepperAndSaltNoise(img, levelOfPepperAndSaltNoise)

        levelOfRotation = random.uniform(-10, 10)
        img = self.rotateImage(img, levelOfRotation)

        levelOfBrightness = random.uniform(0.7, 1.3)
        img = self.changeBrightness(img, levelOfBrightness)

        levelOfContrast = random.uniform(0.7, 1.3)
        img = self.changeContrast(img, levelOfContrast)

        if trainOrValid == "train":
            imagePath = f"{self.DATA_SET_OCR_DIR}/train/images/{fileName}.png"
            labelPath = f"{self.DATA_SET_OCR_DIR}/train/labels/{fileName}.txt"
        else:
            imagePath = f"{self.DATA_SET_OCR_DIR}/valid/images/{fileName}.png"
            labelPath = f"{self.DATA_SET_OCR_DIR}/valid/labels/{fileName}.txt"

        img.save(imagePath)
        with open(labelPath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(yoloLabels))

    def makeGaussianNoise(self, licensePlateImage, levelOfGaussianNoise):
        npImage = np.array(licensePlateImage)
        noise = np.random.normal(0, levelOfGaussianNoise, npImage.shape).astype('int16')
        noisyImgArray = npImage.astype('int16') + noise
        noisyImgArray = np.clip(noisyImgArray, 0, 255).astype('uint8')
        noisyImage = Image.fromarray(noisyImgArray)
        return noisyImage
    
    def makePepperAndSaltNoise(self, licensePlateImage, levelOfPepperAndSaltNoise):
        if levelOfPepperAndSaltNoise == 0:
            return licensePlateImage

        npImage = np.array(licensePlateImage)
        saltVsPepper = 0.5
        amount = 0.004 * levelOfPepperAndSaltNoise

        saltNumber = np.ceil(amount * npImage.size * saltVsPepper)
        coords = [np.random.randint(0, i - 1, int(saltNumber)) for i in npImage.shape]
        npImage[coords[0], coords[1], :] = 255

        pepperNumber = np.ceil(amount * npImage.size * (1. - saltVsPepper))
        coords = [np.random.randint(0, i - 1, int(pepperNumber)) for i in npImage.shape]
        npImage[coords[0], coords[1], :] = 0

        noisyImage = Image.fromarray(npImage)
        return noisyImage
    
    def rotateImage(self, licensePlateImage, levelOfRotation):
        fillColorR = random.randint(0, 255)
        fillColorG = random.randint(0, 255)
        fillColorB = random.randint(0, 255)
        return licensePlateImage.rotate(levelOfRotation, expand=True, fillcolor=(fillColorR, fillColorG, fillColorB))

    def changeBrightness(self, licensePlateImage, levelOfBrightness):
        enhancer = ImageEnhance.Brightness(licensePlateImage)
        enhancedImage = enhancer.enhance(levelOfBrightness)
        return enhancedImage
    
    def changeContrast(self, licensePlateImage, levelOfContrast):
        enhancer = ImageEnhance.Contrast(licensePlateImage)
        enhancedImage = enhancer.enhance(levelOfContrast)
        return enhancedImage