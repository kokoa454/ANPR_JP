__package__ = "DATA_SET_OCR"

import random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os
import numpy as np
import shutil

class DATA_SET_OCR:
    DATA_SET_OCR_DIR = "./data_set_ocr"
    YOLO_DATA_YAML_PATH = DATA_SET_OCR_DIR + "/data.yaml"
    
    TYPE_OF_VEHICLE_LIST = ["普通_自家用", "普通_事業用", "軽_自家用", "軽_事業用"]
    TYPE_OF_VEHICLE_ROMAN = {
        "普通_自家用": "F_JIKAYO",
        "普通_事業用": "F_JIGYOYO",
        "軽_自家用": "K_JIKAYO",
        "軽_事業用": "K_JIGYOYO"
    }

    LICENSE_PLATE_WIDTH = 440
    LICENSE_PLATE_HEIGHT = 220
    
    ALPHABET_LIST = ["A", "C", "F", "H", "K", "L", "M", "P", "X", "Y"]
    
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
    CHARACTER_NAMES.extend(TYPE_OF_VEHICLE_LIST)
    CHARACTER_NAMES.extend(OFFICE_CODE_LIST)
    CHARACTER_NAMES.extend([str(i) for i in range(10)])
    CHARACTER_NAMES.extend(ALPHABET_LIST)
    CHARACTER_NAMES.extend(HIRAGANA_LIST_ALL)
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

        vehicleTypesNumber = len(self.TYPE_OF_VEHICLE_LIST)
        fileNameLength = len(str(trainingNumber)) + 1

        for typeOfVehicle in range(vehicleTypesNumber):
            currentImageCount = 0
            for imageNumber in range(1, trainNumber + 1):
                plateBackGroundColor = self.getPlateBackgroundColor(typeOfVehicle)
                plateTextColor = self.getPlateTextColor(typeOfVehicle)
                officeCode = self.getOfficeCode()
                classNumber = self.getClassNumber(typeOfVehicle)
                hiraganaCode = self.getHiraganaCode(typeOfVehicle)
                registrationNumber = self.getRegistrationNumber()

                fileName = f"train_{self.TYPE_OF_VEHICLE_ROMAN[self.TYPE_OF_VEHICLE_LIST[typeOfVehicle]]}_{imageNumber:0{fileNameLength}}" 
                self.generatePlate(fileName, "train", typeOfVehicle, plateBackGroundColor, plateTextColor, officeCode, classNumber, hiraganaCode, registrationNumber)

                currentImageCount += 1
                progress = int(currentImageCount / trainNumber * 50)
                bar = "█" * progress + "-" * (50 - progress)
                print(f"\r[{bar}] {currentImageCount}/{trainNumber} | {self.TYPE_OF_VEHICLE_LIST[typeOfVehicle]} | train", end="", flush=True)
            
            print("\n")

            currentImageCount = 0
            for imageNumber in range(1, validationNumber + 1):
                plateBackGroundColor = self.getPlateBackgroundColor(typeOfVehicle)
                plateTextColor = self.getPlateTextColor(typeOfVehicle)
                officeCode = self.getOfficeCode()
                classNumber = self.getClassNumber(typeOfVehicle)
                hiraganaCode = self.getHiraganaCode(typeOfVehicle)
                registrationNumber = self.getRegistrationNumber()

                fileName = f"valid_{self.TYPE_OF_VEHICLE_ROMAN[self.TYPE_OF_VEHICLE_LIST[typeOfVehicle]]}_{imageNumber:0{fileNameLength}}" 
                self.generatePlate(fileName, "valid", typeOfVehicle, plateBackGroundColor, plateTextColor, officeCode, classNumber, hiraganaCode, registrationNumber)

                currentImageCount += 1
                progress = int(currentImageCount / validationNumber * 50)
                bar = "█" * progress + "-" * (50 - progress)
                print(f"\r[{bar}] {currentImageCount}/{validationNumber} | {self.TYPE_OF_VEHICLE_LIST[typeOfVehicle]} | valid", end="", flush=True)
            
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
        
    def getPlateBackgroundColor(self, typeOfVehicle):
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

    def getYoloBboxFromAbsolute(self, xMin, yMin, xMax, yMax, width, height):
        xCenter = ((xMin + xMax) / 2) / width
        yCenter = ((yMin + yMax) / 2) / height
        w = (xMax - xMin) / width
        h = (yMax - yMin) / height
        return xCenter, yCenter, w, h

    def generatePlate(self, fileName, trainOrValid, typeOfVehicle, plateBackgroundColor, plateTextColor, officeCode, classNumber, hiraganaCode, registrationNumber):
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

        yoloLabels = []
        
        img = Image.new("RGB", (WIDTH, HEIGHT), plateBackgroundColor[1])
        draw = ImageDraw.Draw(img)

        draw.rectangle([(0, 0), (WIDTH - 1, HEIGHT - 1)], outline = COLOR_FOR_FRAME, width = MARGIN)
        draw.ellipse([(80 - RADIUS, 30 - RADIUS), (80 + RADIUS, 30 + RADIUS)], fill = COLOR_FOR_FRAME)
        draw.ellipse([(360 - RADIUS, 30 - RADIUS), (360 + RADIUS, 30 + RADIUS)], fill = COLOR_FOR_FRAME)

        licensePlateType = self.TYPE_OF_VEHICLE_LIST[typeOfVehicle]
        licensePlateTypeId = self.NAME_TO_ID[licensePlateType]
        plateXCenter, plateYCenter, plateW, plateH = self.getYoloBboxFromAbsolute(
            0, 0, WIDTH, HEIGHT, WIDTH, HEIGHT
            )
        yoloLabels.append(f"{licensePlateTypeId} {plateXCenter:.6f} {plateYCenter:.6f} {plateW:.6f} {plateH:.6f}")

        for font in [FONT_HIRAGINO, FONT_TRM, FONT_FZ]:
            if not os.path.exists(font):
                raise FileNotFoundError(f"ERROR: フォントファイル '{font}' が見つかりません。")
            
        dummyImg = Image.new("RGB", (1, 1))
        dummyDraw = ImageDraw.Draw(dummyImg)

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

        officeCodeClassId = self.NAME_TO_ID[officeCode]
        officeCodeXCenter, officeCodeYCenter, officeCodeW, officeCodeH = self.getYoloBboxFromAbsolute(
            bboxOffice[0], bboxOffice[1], bboxOffice[2], bboxOffice[3], WIDTH, HEIGHT
        )
        yoloLabels.append(f"{officeCodeClassId} {officeCodeXCenter:.6f} {officeCodeYCenter:.6f} {officeCodeW:.6f} {officeCodeH:.6f}")


        fontClassNumber = ImageFont.truetype(FONT_HIRAGINO, FONT_SIZE_CLASS)
        positionForClassNumber = [230, 10]
        CHAR_SPACING = 36

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
                
                xMin = int(currentX)
                yMin = yPos
                xMax = int(currentX) + newWidth
                yMax = yPos + textImage.height
            else:
                draw.text((currentX, yPos), char, font=fontClassNumber, stroke_width=int(THICKNESS_CLASS), fill=plateTextColor[1])
                bbox = draw.textbbox((currentX, yPos), char, font=fontClassNumber, stroke_width=int(THICKNESS_CLASS))
                xMin, yMin, xMax, yMax = bbox

            xCenter, yCenter, w, h = self.getYoloBboxFromAbsolute(xMin, yMin, xMax, yMax, WIDTH, HEIGHT)
            yoloLabels.append(f"{charClassId} {xCenter:.6f} {yCenter:.6f} {w:.6f} {h:.6f}")
            
            currentX += CHAR_SPACING

        positionForHiraganaCode = [20, 110]
        fontSizeForHiraganaCode = 55
        fontHiraganaCode = ImageFont.truetype(FONT_FZ, fontSizeForHiraganaCode)

        if hiraganaCode in ["あ", "い", "う", "か", "き", "く", "け", "こ", "せ", "を"]:
            positionForHiraganaCode = [16, 55]
            fontSizeForHiraganaCode = 180
            fontHiraganaCode = ImageFont.truetype(FONT_TRM, fontSizeForHiraganaCode)

        draw.text(positionForHiraganaCode, hiraganaCode, font=fontHiraganaCode, fill=plateTextColor[1])

        bboxHiragana = draw.textbbox(positionForHiraganaCode, hiraganaCode, font=fontHiraganaCode)
        hiraganaClassId = self.NAME_TO_ID[hiraganaCode]
        hiraganaXCenter, hiraganaYCenter, hiraganaW, hiraganaH = self.getYoloBboxFromAbsolute(
            bboxHiragana[0], bboxHiragana[1], bboxHiragana[2], bboxHiragana[3], WIDTH, HEIGHT
        )
        yoloLabels.append(f"{hiraganaClassId} {hiraganaXCenter:.6f} {hiraganaYCenter:.6f} {hiraganaW:.6f} {hiraganaH:.6f}")


        fontSizeForRegistrationNumber = 130
        fontRegistrationNumber = ImageFont.truetype(FONT_TRM, fontSizeForRegistrationNumber)
        positionForRegistrationNumber = [80, 80]
        REGISTRATION_NUMBER_WIDTH = 60
        
        currentX = positionForRegistrationNumber[0]
        yPos = positionForRegistrationNumber[1]

        for char in registrationNumber:
            charClassId = self.NAME_TO_ID[char]
            
            xPos = currentX

            if char == '-':
                lineWidth = 10
                lineLength = 30
                centerX = xPos + REGISTRATION_NUMBER_WIDTH / 2
                centerY = yPos + fontSizeForRegistrationNumber / 2
                
                draw.line(
                    (centerX - lineLength/2, centerY, centerX + lineLength/2, centerY),
                    fill=plateTextColor[1], width=lineWidth
                )

                xMinHyphen = centerX - lineLength/2
                yMinHyphen = centerY - lineWidth/2
                xMaxHyphen = centerX + lineLength/2
                yMaxHyphen = centerY + lineWidth/2
                
                xCenter, yCenter, w, h = self.getYoloBboxFromAbsolute(
                    xMinHyphen, yMinHyphen, xMaxHyphen, yMaxHyphen, WIDTH, HEIGHT
                )
                yoloLabels.append(f"{charClassId} {xCenter:.6f} {yCenter:.6f} {w:.6f} {h:.6f}")
                currentX += REGISTRATION_NUMBER_WIDTH
                continue

            elif char == '・':
                dotRadius = 6
                dotCenterX = xPos + REGISTRATION_NUMBER_WIDTH / 2
                dotCenterY = yPos + fontSizeForRegistrationNumber * 0.4
                
                draw.ellipse(
                    [(dotCenterX - dotRadius, dotCenterY - dotRadius),
                    (dotCenterX + dotRadius, dotCenterY + dotRadius)],
                    fill=plateTextColor[1]
                )
                
                xMinDot = dotCenterX - dotRadius
                yMinDot = dotCenterY - dotRadius
                xMaxDot = dotCenterX + dotRadius
                yMaxDot = dotCenterY + dotRadius
                
                xCenter, yCenter, w, h = self.getYoloBboxFromAbsolute(
                    xMinDot, yMinDot, xMaxDot, yMaxDot, WIDTH, HEIGHT
                )
                yoloLabels.append(f"{charClassId} {xCenter:.6f} {yCenter:.6f} {w:.6f} {h:.6f}")
                currentX += REGISTRATION_NUMBER_WIDTH
                continue

            draw.text((xPos, yPos), char, font=fontRegistrationNumber, fill=plateTextColor[1])
            
            bboxRegistrationChar = draw.textbbox((xPos, yPos), char, font=fontRegistrationNumber)
            
            xCenter, yCenter, w, h = self.getYoloBboxFromAbsolute(
                bboxRegistrationChar[0], bboxRegistrationChar[1], bboxRegistrationChar[2], bboxRegistrationChar[3], WIDTH, HEIGHT
            )
            yoloLabels.append(f"{charClassId} {xCenter:.6f} {yCenter:.6f} {w:.6f} {h:.6f}")
            currentX += REGISTRATION_NUMBER_WIDTH

        levelOfGaussianNoise = random.randint(0, 50)
        img = self.makeGaussianNoise(img, levelOfGaussianNoise)

        levelOfBlur = random.randint(0, 4)
        img = self.makeBlur(img, levelOfBlur)

        levelOfMotionBlur = random.randint(0, 5)
        img = self.makeMotionBlur(img, levelOfMotionBlur)

        levelOfPepperAndSaltNoise = random.randint(0, 2)
        img = self.makePepperAndSaltNoise(img, levelOfPepperAndSaltNoise)

        levelOfRotation = random.uniform(-10, 10)
        img = self.rotateImage(img, levelOfRotation)

        levelOfBrightness = random.uniform(0.5, 1.3)
        img = self.changeBrightness(img, levelOfBrightness)

        levelOfContrast = random.uniform(0.5, 1.3)
        img = self.changeContrast(img, levelOfContrast)

        levelOfPerspectiveUp = random.uniform(-40, 40)
        levelOfPerspectiveDown = random.uniform(-40, 40)
        levelOfPerspectiveRight = random.uniform(-40, 40)
        levelOfPerspectiveLeft = random.uniform(-40, 40)

        img, perspective = self.makePerspectiveTransform(
            img, 
            levelOfPerspectiveUp, 
            levelOfPerspectiveDown, 
            levelOfPerspectiveRight, 
            levelOfPerspectiveLeft
        )
        
        yoloLabels = self.transformYoloBbox(yoloLabels, perspective, WIDTH, HEIGHT)
        
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

    def makeBlur(self, licensePlateImage, levelOfBlur):
        if levelOfBlur == 0:
            return licensePlateImage
        blurredImage = licensePlateImage.filter(ImageFilter.GaussianBlur(radius=levelOfBlur))
        return blurredImage
    
    def makeMotionBlur(self, licensePlateImage, levelOfMotionBlur):
        if levelOfMotionBlur == 0:
            return licensePlateImage
        blurredImage = licensePlateImage.filter(ImageFilter.BoxBlur(radius=levelOfMotionBlur))
        return blurredImage
    
    def makePepperAndSaltNoise(self, licensePlateImage, levelOfPepperAndSaltNoise):
        if levelOfPepperAndSaltNoise == 0:
            return licensePlateImage

        npImage = np.array(licensePlateImage)
        saltVsPepper = 0.5
        amount = 0.004 * levelOfPepperAndSaltNoise

        saltNumber = np.ceil(amount * npImage.size * saltVsPepper)
        coordinates = [np.random.randint(0, i - 1, int(saltNumber)) for i in npImage.shape]
        npImage[coordinates[0], coordinates[1], :] = 255

        pepperNumber = np.ceil(amount * npImage.size * (1. - saltVsPepper))
        coordinates = [np.random.randint(0, i - 1, int(pepperNumber)) for i in npImage.shape]
        npImage[coordinates[0], coordinates[1], :] = 0

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
    
    def makePerspectiveTransform(self, licensePlateImage, levelOfPerspectiveUp, levelOfPerspectiveDown, levelOfPerspectiveRight, levelOfPerspectiveLeft):
        width, height = licensePlateImage.size
        
        maxRandomOffset = int(max(width, height) * 0.12)
        
        maxOffsetUp = int(abs(levelOfPerspectiveUp) / 45 * maxRandomOffset)
        maxOffsetDown = int(abs(levelOfPerspectiveDown) / 45 * maxRandomOffset)
        maxOffsetRight = int(abs(levelOfPerspectiveRight) / 45 * maxRandomOffset)
        maxOffsetLeft = int(abs(levelOfPerspectiveLeft) / 45 * maxRandomOffset)
        
        if maxOffsetUp < 1 and maxOffsetDown < 1 and maxOffsetRight < 1 and maxOffsetLeft < 1:
            H = np.eye(3)
            return licensePlateImage, H

        topLeftXOffset = random.randint(-maxOffsetLeft, maxOffsetLeft)
        topLeftYOffset = random.randint(-maxOffsetUp, maxOffsetUp)
        
        topRightXOffset = random.randint(-maxOffsetRight, maxOffsetRight)
        topRightYOffset = random.randint(-maxOffsetUp, maxOffsetUp)

        bottomRightXOffset = random.randint(-maxOffsetRight, maxOffsetRight)
        bottomRightYOffset = random.randint(-maxOffsetDown, maxOffsetDown)

        bottomLeftXOffset = random.randint(-maxOffsetLeft, maxOffsetLeft)
        bottomLeftYOffset = random.randint(-maxOffsetDown, maxOffsetDown)
        
        sourcePointsAbs = [
            0, 0, 
            width, 0, 
            width, height, 
            0, height
        ]
        
        targetPointsAbs = [
            0 + topLeftXOffset, 0 + topLeftYOffset,
            width + topRightXOffset, 0 + topRightYOffset,
            width + bottomRightXOffset, height + bottomRightYOffset,
            0 + bottomLeftXOffset, height + bottomLeftYOffset
        ]

        coeffs = self.calculatePerspectiveCoeffs(sourcePointsAbs, targetPointsAbs)
        
        fillColorR = random.randint(0, 255)
        fillColorG = random.randint(0, 255)
        fillColorB = random.randint(0, 255)
        fillcolor = (fillColorR, fillColorG, fillColorB)
        
        try:
            transformedImage = licensePlateImage.transform(
                (width, height),
                Image.Resampling.PERSPECTIVE,
                data = coeffs,
                fillcolor=fillcolor
            )
        except AttributeError:
            transformedImage = licensePlateImage.transform(
                (width, height),
                Image.PERSPECTIVE,
                data = coeffs,
                fillcolor=fillcolor
            )
        
        homographyInverseMatrix = np.array([
            [coeffs[0], coeffs[1], coeffs[2]],
            [coeffs[3], coeffs[4], coeffs[5]],
            [coeffs[6], coeffs[7], 1.0]
        ])
        H = np.linalg.inv(homographyInverseMatrix)
        
        return transformedImage, H

    def transformYoloBbox(self, yoloLabels, perspective, width, height):
        newYoloLabels = []
        
        for label in yoloLabels:
            parts = label.split()
            classId = parts[0]
            xCenter, yCenter, w, h = [float(p) for p in parts[1:]]
            
            xMinNorm = xCenter - w/2
            yMinNorm = yCenter - h/2
            xMaxNorm = xCenter + w/2
            yMaxNorm = yCenter + h/2

            xMinAbs = xMinNorm * width
            yMinAbs = yMinNorm * height
            xMaxAbs = xMaxNorm * width
            yMaxAbs = yMaxNorm * height

            cornersAbs = np.array([
                [xMinAbs, yMinAbs, 1],
                [xMaxAbs, yMinAbs, 1],
                [xMaxAbs, yMaxAbs, 1],
                [xMinAbs, yMaxAbs, 1]
            ]).T

            transformedCorners = perspective @ cornersAbs
            
            widthAndHeight = transformedCorners[2, :]
            transformedCorners = transformedCorners[:2, :] / widthAndHeight

            minX, maxX = np.min(transformedCorners[0, :]), np.max(transformedCorners[0, :])
            minY, maxY = np.min(transformedCorners[1, :]), np.max(transformedCorners[1, :])

            newXMinAbs = np.clip(minX, 0, width)
            newYMinAbs = np.clip(minY, 0, height)
            newXMaxAbs = np.clip(maxX, 0, width)
            newYMaxAbs = np.clip(maxY, 0, height)

            newXCenter, newYCenter, newW, newH = self.getYoloBboxFromAbsolute(
                newXMinAbs, newYMinAbs, newXMaxAbs, newYMaxAbs, width, height
            )

            newYoloLabels.append(f"{classId} {newXCenter:.6f} {newYCenter:.6f} {newW:.6f} {newH:.6f}")

        return newYoloLabels
    
    def calculatePerspectiveCoeffs(self, sourcePointsAbs, targetPointsAbs):
        src = np.array(sourcePointsAbs, dtype=np.float32).reshape(-1, 2)
        dst = np.array(targetPointsAbs, dtype=np.float32).reshape(-1, 2)

        A = np.zeros((8, 8), dtype=np.float64)
        b = np.zeros((8,), dtype=np.float64)
        
        for i in range(4):
            x, y = src[i]
            xPrime, yPrime = dst[i]
            
            A[i * 2, 0] = x
            A[i * 2, 1] = y
            A[i * 2, 2] = 1
            A[i * 2, 6] = -xPrime * x
            A[i * 2, 7] = -xPrime * y
            b[i * 2] = xPrime
            
            A[i * 2 + 1, 3] = x
            A[i * 2 + 1, 4] = y
            A[i * 2 + 1, 5] = 1
            A[i * 2 + 1, 6] = -yPrime * x
            A[i * 2 + 1, 7] = -yPrime * y
            b[i * 2 + 1] = yPrime

        try:
            coeffs = np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            return (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0)

        return tuple(coeffs)