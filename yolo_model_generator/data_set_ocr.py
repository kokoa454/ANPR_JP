import random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os
import numpy as np
import shutil

# -- OCR用データセット生成クラス --
class DATA_SET_OCR:
    DATA_SET_OCR_DIR = "./data_set_ocr"
    YOLO_DATA_YAML_PATH = DATA_SET_OCR_DIR + "/data.yaml"
    
    # 車種別リストと対応ローマ字
    TYPE_OF_VEHICLE_LIST = ["普通_自家用", "普通_事業用", "軽_自家用", "軽_事業用"]
    TYPE_OF_VEHICLE_ROMAN = {
        "普通_自家用": "F_JIKAYO",
        "普通_事業用": "F_JIGYOYO",
        "軽_自家用": "K_JIKAYO",
        "軽_事業用": "K_JIGYOYO"
    }

    # ナンバープレート寸法
    NUMBER_PLATE_WIDTH = 440
    NUMBER_PLATE_HEIGHT = 220

    # ナンバープレート背景色リスト
    NUMBER_PLATE_BG_COLOR_LIST = [
            ("white", (240, 240, 240)),
            ("green", (0, 60, 0)),
            ("yellow", (255, 255, 0)),
            ("black", (0, 0, 0))
    ]

    # ナンバープレート文字色リスト
    NUMBER_PLATE_TEXT_COLOR_LIST = [
            ("green", (0, 60, 0)),
            ("white", (240, 240, 240)),
            ("black", (0, 0, 0)),
            ("yellow", (255, 255, 0))
    ]
    
    # 分類番号のアルファベットリスト
    ALPHABET_LIST = ["A", "C", "F", "H", "K", "L", "M", "P", "X", "Y"]
    
    # 地名コード
    PLACE_CODE_LIST = [
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
        "千葉","習志野","成田","柏","袖ヶ浦","野田","松戸","船橋","市原","市川",
        "板橋","練馬","足立","江東","品川","多摩","八王子","江戸川","世田谷","杉並","葛飾",
        "横浜","川崎","相模","湘南",
        "山梨","富士山",
        "新潟","長岡","上越","長野","松本","諏訪","南信州","安曇野",
        "富山","石川","金沢",
        "福井",
        "岐阜","飛騨",
        "静岡","浜松","沼津","伊豆",
        "名古屋","三河","岡崎","豊田","尾張小牧","一宮","春日井","豊橋",
        "三重","鈴鹿","伊勢志摩","四日市",
        "滋賀",
        "京都",
        "大阪","なにわ","和泉","堺",
        "奈良","飛鳥",
        "和歌山",
        "神戸","姫路",
        "鳥取",
        "島根","出雲",
        "岡山","倉敷",
        "広島","福山",
        "山口","下関",
        "徳島",
        "香川","高松",
        "愛媛",
        "高知",
        "福岡","北九州","久留米","筑豊",
        "佐賀",
        "長崎","佐世保",
        "熊本",
        "大分",
        "宮崎",
        "鹿児島","奄美",
        "沖縄"
    ]

    # ひらがなリスト
    HIRAGANA_LIST_F_JIKAYO = ["さ", "す", "せ", "そ", "た", "ち", "つ", "て", "と", "な", "に", "ぬ", "ね", "の", "は", "ひ", "ふ", "ほ", "ま", "み", "む", "め", "も", "や", "ゆ", "ら", "り", "る", "ろ"]
    HIRAGANA_LIST_F_JIGYOYO = ["あ", "い", "う", "え", "か", "き", "く", "け", "こ", "れ", "わ"]
    HIRAGANA_LIST_K_JIKAYO = ["あ", "い", "う", "え", "か", "き", "く", "け", "こ", "さ", "す", "せ", "そ", "た", "ち", "つ", "て", "と", "な", "に", "ぬ", "ね", "の", "は", "ひ", "ふ", "ほ", "ま", "み", "む", "め", "も", "や", "ゆ", "よ", "ら", "る", "ろ"]
    HIRAGANA_LIST_K_JIGYOYO = ["り", "れ", "わ"]

    # 全てのひらがなリスト
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

    # 特殊文字リスト
    SPECIAL_CHARACTER_LIST = ["・", "-"]

    # YOLO用クラス名リスト
    CHARACTER_NAMES = []
    CHARACTER_NAMES.extend(PLACE_CODE_LIST)
    CHARACTER_NAMES.extend([str(i) for i in range(10)])
    CHARACTER_NAMES.extend(ALPHABET_LIST)
    CHARACTER_NAMES.extend(HIRAGANA_LIST_ALL)
    CHARACTER_NAMES.extend(SPECIAL_CHARACTER_LIST)

    # YOLO用クラスIDリスト
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

        # トレーニングデータ生成
        for typeOfVehicle in range(vehicleTypesNumber):
            currentImageCount = 0

            for imageNumber in range(1, trainNumber + 1):
                numberPlateBGColor = self.getPlateBackgroundColor(typeOfVehicle)
                numberPlateTextColor = self.getPlateTextColor(typeOfVehicle)
                placeCode = self.getPlaceCode()
                classNum = self.getClassNum(typeOfVehicle)
                hiraganaCode = self.getHiraganaCode(typeOfVehicle)
                regNum = self.getRegNum()

                fileName = f"train_{self.TYPE_OF_VEHICLE_ROMAN[self.TYPE_OF_VEHICLE_LIST[typeOfVehicle]]}_{imageNumber:0{fileNameLength}}" 
                self.generatePlate(fileName, "train", typeOfVehicle, numberPlateBGColor, numberPlateTextColor, placeCode, classNum, hiraganaCode, regNum)

                currentImageCount += 1

                progress = int(currentImageCount / trainNumber * 50)
                bar = "█" * progress + "-" * (50 - progress)
                print(f"\r[{bar}] {currentImageCount}/{trainNumber} | {self.TYPE_OF_VEHICLE_LIST[typeOfVehicle]} | train", end="", flush=True)
            
            print("\n")

            currentImageCount = 0

            # バリデーションデータ生成
            for imageNumber in range(1, validationNumber + 1):
                numberPlateBGColor = self.getPlateBackgroundColor(typeOfVehicle)
                numberPlateTextColor = self.getPlateTextColor(typeOfVehicle)
                placeCode = self.getPlaceCode()
                classNum = self.getClassNum(typeOfVehicle)
                hiraganaCode = self.getHiraganaCode(typeOfVehicle)
                regNum = self.getRegNum()

                fileName = f"valid_{self.TYPE_OF_VEHICLE_ROMAN[self.TYPE_OF_VEHICLE_LIST[typeOfVehicle]]}_{imageNumber:0{fileNameLength}}" 
                self.generatePlate(fileName, "valid", typeOfVehicle, numberPlateBGColor, numberPlateTextColor, placeCode, classNum, hiraganaCode, regNum)

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
        return self.NUMBER_PLATE_BG_COLOR_LIST[typeOfVehicle]

    def getPlateTextColor(self, typeOfVehicle):
        return self.NUMBER_PLATE_TEXT_COLOR_LIST[typeOfVehicle]
    
    def getPlaceCode(self):
        return random.choice(self.PLACE_CODE_LIST)

    def getClassNum(self, typeOfVehicle):        
        if typeOfVehicle in (0, 1):
            classNum = str(random.choice([1, 2, 3, 8, 9, 0]))
            randomNum = random.randint(0, 1)

            if randomNum == 0:
                classNum += str(random.randint(0, 9))
            else:
                randomNum = random.randint(0, 2)
                
                if randomNum == 0:
                    classNum += str(random.randint(0, 9))
                    classNum += str(random.randint(0, 9))
                elif randomNum == 1:
                    classNum += str(random.randint(0, 9))
                    classNum += random.choice(self.ALPHABET_LIST)
                else:
                    classNum += random.choice(self.ALPHABET_LIST)
                    classNum += random.choice(self.ALPHABET_LIST)

        else:
            classNum = str(random.choice([4, 5, 6, 7, 8]))
            randomNum = random.randint(0, 1)
            
            if randomNum == 0:
                classNum += str(random.randint(0, 9))
            else:
                randomNum = random.randint(0, 2)

                if randomNum == 0:
                    classNum += str(random.randint(0, 9))
                    classNum += str(random.randint(0, 9))
                elif randomNum == 1:
                    classNum += str(random.randint(0, 9))
                    classNum += random.choice(self.ALPHABET_LIST)
                else:
                    classNum += random.choice(self.ALPHABET_LIST)
                    classNum += random.choice(self.ALPHABET_LIST)

        return classNum

    def getHiraganaCode(self, typeOfVehicle):
        if typeOfVehicle == 0:
            hiraganaList = self.HIRAGANA_LIST_F_JIKAYO
        elif typeOfVehicle == 1:
            hiraganaList = self.HIRAGANA_LIST_F_JIGYOYO
        elif typeOfVehicle == 2:
            hiraganaList = self.HIRAGANA_LIST_K_JIKAYO
        else:
            hiraganaList = self.HIRAGANA_LIST_K_JIGYOYO

        return random.choice(hiraganaList)

    def getRegNum(self):
        prefixRegNum = random.randint(1, 99)
        
        if prefixRegNum < 10:
            regNum = self.SPECIAL_CHARACTER_LIST[0] + str(prefixRegNum)
        else:
            regNum = str(prefixRegNum)

        regNum += self.SPECIAL_CHARACTER_LIST[1]
        regNum += f"{random.randint(0, 99):02d}"

        return regNum

    def generatePlate(self, fileName, trainOrValid, typeOfVehicle, numberPlateBGColor, numberPlateTextColor, placeCode, classNum, hiraganaCode, regNum):
        FONT1 = "./fonts/HiraginoMaruGothicProNW4.otf"
        FONT2 = "./fonts/TrmFontJB.ttf"
        FONT3 = "./fonts/FZcarnumberJA.otf"
        # FONT3 = "./fonts/HOTKaishokkR.otf"

        MARGIN = 4
        RADIUS = 6
        COLOR_FOR_FRAME = (128, 128, 128)
        
        FONT_SIZE_OFFICE = 55
        THICKNESS_OFFICE = 1.2
        FONT_SIZE_CLASS = 58
        THICKNESS_CLASS = 1.2

        yoloLabels = []
        
        # ナンバープレート画像生成
        img = Image.new("RGB", (self.NUMBER_PLATE_WIDTH, self.NUMBER_PLATE_HEIGHT), numberPlateBGColor[1])
        draw = ImageDraw.Draw(img)

        # ナンバープレート枠とネジ描画
        draw.rectangle([(0, 0), (self.NUMBER_PLATE_WIDTH - 1, self.NUMBER_PLATE_HEIGHT - 1)], outline = COLOR_FOR_FRAME, width = MARGIN)
        draw.ellipse([(80 - RADIUS, 30 - RADIUS), (80 + RADIUS, 30 + RADIUS)], fill = COLOR_FOR_FRAME)
        draw.ellipse([(360 - RADIUS, 30 - RADIUS), (360 + RADIUS, 30 + RADIUS)], fill = COLOR_FOR_FRAME)

        # 地名コード描画開始
        for font in [FONT1, FONT2, FONT1]:
            if not os.path.exists(font):
                raise FileNotFoundError(f"ERROR: フォントファイル '{font}' が見つかりません。")
            
        dummyImg = Image.new("RGB", (1, 1))
        dummyDraw = ImageDraw.Draw(dummyImg)

        fontPlaceCode = ImageFont.truetype(FONT1, FONT_SIZE_OFFICE)
        positionForPlaceCode = [105, 10]
        
        if len(placeCode) < 2:
            positionForPlaceCode[0] = 120
            draw.text(positionForPlaceCode, placeCode, font=fontPlaceCode, stroke_width=int(THICKNESS_OFFICE), fill=numberPlateTextColor[1])
            bboxPlace = draw.textbbox(positionForPlaceCode, placeCode, font=fontPlaceCode, stroke_width=int(THICKNESS_OFFICE))
        
        elif len(placeCode) <= 2:
            positionForPlaceCode[0] = 105
            draw.text(positionForPlaceCode, placeCode, font=fontPlaceCode, stroke_width=int(THICKNESS_OFFICE), fill=numberPlateTextColor[1])
            bboxPlace = draw.textbbox(positionForPlaceCode, placeCode, font=fontPlaceCode, stroke_width=int(THICKNESS_OFFICE))
            
        else:
            compressRatio = 0.7 if len(placeCode) == 3 else 0.55
            positionForPlaceCode[0] = 105

            bbox = dummyDraw.textbbox((0, 0), placeCode, font=fontPlaceCode, stroke_width=int(THICKNESS_OFFICE))
            textWidth = bbox[2] - bbox[0]
            textHeight = bbox[3] - bbox[1]

            textImage = Image.new("RGBA", (textWidth, textHeight), (0, 0, 0, 0))
            textDraw = ImageDraw.Draw(textImage)
            textDraw.text((0, 0), placeCode, font=fontPlaceCode, stroke_width=int(THICKNESS_OFFICE), fill=numberPlateTextColor[1])

            newWidth = int(textImage.width * compressRatio)
            resizedTextImage = textImage.resize((newWidth, textImage.height), Image.Resampling.LANCZOS)

            img.paste(resizedTextImage, positionForPlaceCode, resizedTextImage)
            
            bboxPlace = (positionForPlaceCode[0], positionForPlaceCode[1], positionForPlaceCode[0] + newWidth, positionForPlaceCode[1] + textImage.height)

        # YOLOに地名コードのラベル付け
        placeCodeClassId = self.NAME_TO_ID[placeCode]
        placeCodeXCenter, placeCodeYCenter, placeCodeWidth, placeCodeHeight = self.getYoloBboxFromAbsolute(
            bboxPlace[0], bboxPlace[1], bboxPlace[2], bboxPlace[3], self.NUMBER_PLATE_WIDTH, self.NUMBER_PLATE_HEIGHT
        )
        yoloLabels.append(f"{placeCodeClassId} {placeCodeXCenter:.6f} {placeCodeYCenter:.6f} {placeCodeWidth:.6f} {placeCodeHeight:.6f}")


        # 分類番号描画開始
        fontClassNum = ImageFont.truetype(FONT1, FONT_SIZE_CLASS)
        positionForClassNum = [230, 10]
        CHAR_SPACING = 36

        if len(classNum) == 2:
            positionForClassNum[0] = 260
            
        hasSpecialChar = any(char in classNum for char in ["M", "W", "H", "X"]) and len(classNum) == 3
        
        currentX = positionForClassNum[0]
        yPos = positionForClassNum[1]

        for char in classNum:
            # 横幅が大きい文字の場合は圧縮して描画
            if hasSpecialChar and char in ["M", "W", "H", "X"]:
                bboxChar = dummyDraw.textbbox((0, 0), char, font=fontClassNum, stroke_width=int(THICKNESS_CLASS))
                textWidth = bboxChar[2] - bboxChar[0]
                textHeight = bboxChar[3] - bboxChar[1]

                padding = 10
                textImage = Image.new("RGBA", (textWidth, textHeight + padding), (0, 0, 0, 0))
                textDraw = ImageDraw.Draw(textImage)
                textDraw.text((0, 0), char, font=fontClassNum, stroke_width=int(THICKNESS_CLASS), fill=numberPlateTextColor[1])

                compressRatio = 0.9
                newWidth = int(textImage.width * compressRatio)
                resizedTextImage = textImage.resize((newWidth, textImage.height), Image.Resampling.LANCZOS)
                
                img.paste(resizedTextImage, (int(currentX), yPos), resizedTextImage)
                
                xMin = int(currentX)
                yMin = yPos
                xMax = int(currentX) + newWidth
                yMax = yPos + textImage.height
            else:
                draw.text((currentX, yPos), char, font=fontClassNum, stroke_width=int(THICKNESS_CLASS), fill=numberPlateTextColor[1])
                bbox = draw.textbbox((currentX, yPos), char, font=fontClassNum, stroke_width=int(THICKNESS_CLASS))
                xMin, yMin, xMax, yMax = bbox

            # YOLOに分類番号のラベル付け
            classNumClassId = self.NAME_TO_ID[char]
            classNumXCenter, classNumYCenter, classNumWidth, classNumHeight = self.getYoloBboxFromAbsolute(xMin, yMin, xMax, yMax, self.NUMBER_PLATE_WIDTH, self.NUMBER_PLATE_HEIGHT)
            yoloLabels.append(f"{classNumClassId} {classNumXCenter:.6f} {classNumYCenter:.6f} {classNumWidth:.6f} {classNumHeight:.6f}")

            currentX += CHAR_SPACING

        # ひらがなコード描画開始
        positionForHiraganaCode = [10, 100]
        fontSizeForHiraganaCode = 75
        fontHiraganaCode = ImageFont.truetype(FONT3, fontSizeForHiraganaCode)

        if hiraganaCode in ["あ", "い", "う", "か", "き", "く", "け", "こ", "せ", "を"]:
            positionForHiraganaCode = [16, 55]
            fontSizeForHiraganaCode = 180
            fontHiraganaCode = ImageFont.truetype(FONT2, fontSizeForHiraganaCode)

        draw.text(positionForHiraganaCode, hiraganaCode, font=fontHiraganaCode, fill=numberPlateTextColor[1])

        # YOLOにひらがなコードのラベル付け
        bboxHiragana = draw.textbbox(positionForHiraganaCode, hiraganaCode, font=fontHiraganaCode)
        hiraganaCodeClassId = self.NAME_TO_ID[hiraganaCode]
        hiraganaCodeXCenter, hiraganaCodeYCenter, hiraganaCodeWidth, hiraganaCodeHeight = self.getYoloBboxFromAbsolute(
            bboxHiragana[0], bboxHiragana[1], bboxHiragana[2], bboxHiragana[3], self.NUMBER_PLATE_WIDTH, self.NUMBER_PLATE_HEIGHT
        )
        yoloLabels.append(f"{hiraganaCodeClassId} {hiraganaCodeXCenter:.6f} {hiraganaCodeYCenter:.6f} {hiraganaCodeWidth:.6f} {hiraganaCodeHeight:.6f}")

        # 登録番号描画開始
        fontSizeForRegNum = 130
        fontRegNum = ImageFont.truetype(FONT2, fontSizeForRegNum)
        positionForRegNum = [80, 80]
        REGISTRATION_NUMBER_WIDTH = 60
        
        currentX = positionForRegNum[0]
        yPos = positionForRegNum[1]

        for char in regNum:
            regNumClassId = self.NAME_TO_ID[char]
            
            xPos = currentX

            if char == self.SPECIAL_CHARACTER_LIST[0]:
                dotRadius = 6
                dotCenterX = xPos + REGISTRATION_NUMBER_WIDTH / 2
                dotCenterY = yPos + fontSizeForRegNum * 0.4
                
                draw.ellipse(
                    [(dotCenterX - dotRadius, dotCenterY - dotRadius),
                    (dotCenterX + dotRadius, dotCenterY + dotRadius)],
                    fill=numberPlateTextColor[1]
                )
                
                xMinDot = dotCenterX - dotRadius
                yMinDot = dotCenterY - dotRadius
                xMaxDot = dotCenterX + dotRadius
                yMaxDot = dotCenterY + dotRadius

                regNumXCenter, regNumYCenter, regNumWidth, regNumHeight = self.getYoloBboxFromAbsolute(
                    xMinDot, yMinDot, xMaxDot, yMaxDot, self.NUMBER_PLATE_WIDTH, self.NUMBER_PLATE_HEIGHT
                )
                yoloLabels.append(f"{regNumClassId} {regNumXCenter:.6f} {regNumYCenter:.6f} {regNumWidth:.6f} {regNumHeight:.6f}")
                currentX += REGISTRATION_NUMBER_WIDTH

            elif char == self.SPECIAL_CHARACTER_LIST[1]:
                lineWidth = 10
                lineLength = 30
                centerX = xPos + REGISTRATION_NUMBER_WIDTH / 2
                centerY = yPos + fontSizeForRegNum / 2
                
                draw.line(
                    (centerX - lineLength/2, centerY, centerX + lineLength/2, centerY),
                    fill=numberPlateTextColor[1], width=lineWidth
                )

                xMinHyphen = centerX - lineLength/2
                yMinHyphen = centerY - lineWidth/2
                xMaxHyphen = centerX + lineLength/2
                yMaxHyphen = centerY + lineWidth/2

                regNumXCenter, regNumYCenter, regNumWidth, regNumHeight = self.getYoloBboxFromAbsolute(
                    xMinHyphen, yMinHyphen, xMaxHyphen, yMaxHyphen, self.NUMBER_PLATE_WIDTH, self.NUMBER_PLATE_HEIGHT
                )
                yoloLabels.append(f"{regNumClassId} {regNumXCenter:.6f} {regNumYCenter:.6f} {regNumWidth:.6f} {regNumHeight:.6f}")
                currentX += REGISTRATION_NUMBER_WIDTH

            else:
                draw.text((xPos, yPos), char, font=fontRegNum, fill=numberPlateTextColor[1])
                
                bboxRegistrationChar = draw.textbbox((xPos, yPos), char, font=fontRegNum)

                regNumXCenter, regNumYCenter, regNumWidth, regNumHeight = self.getYoloBboxFromAbsolute(
                    bboxRegistrationChar[0], bboxRegistrationChar[1], bboxRegistrationChar[2], bboxRegistrationChar[3], self.NUMBER_PLATE_WIDTH, self.NUMBER_PLATE_HEIGHT
                )
                yoloLabels.append(f"{regNumClassId} {regNumXCenter:.6f} {regNumYCenter:.6f} {regNumWidth:.6f} {regNumHeight:.6f}")
                currentX += REGISTRATION_NUMBER_WIDTH

        # 画像加工処理
        # ガウシアンノイズ付与
        # 50%の確率でノイズを付与
        if random.random() < 0.5:
            levelOfGaussianNoise = random.randint(0, 50)
            img = self.makeGaussianNoise(img, levelOfGaussianNoise)

        # ぼかし付与
        # 50%の確率でぼかしを付与
        if random.random() < 0.5:
            levelOfBlur = random.randint(0, 4)
            img = self.makeBlur(img, levelOfBlur)

        # モーションブラー付与
        # 50%の確率でモーションブラーを付与
        if random.random() < 0.5:
            levelOfMotionBlur = random.randint(0, 5)
            img = self.makeMotionBlur(img, levelOfMotionBlur)

        # ペッパー・ソルトノイズ付与
        # 50%の確率でソルトノイスを付与
        if random.random() < 0.5:
            levelOfPepperAndSaltNoise = random.randint(0, 2)
            img = self.makePepperAndSaltNoise(img, levelOfPepperAndSaltNoise)

        # 雲光付与
        # 50%の確率で雲光を付与
        if random.random() < 0.5:
            maxRadiusRatio = random.uniform(0, 0.8)
            maxIntensity = random.randint(50, 200)
            img = self.makeSunGlare(img, maxRadiusRatio, maxIntensity)

        # 阴影付与
        # 50%の確率で陰影を付与
        if random.random() < 0.5:
            maxOpacity = random.uniform(0, 0.7)
            img = self.makeRandomShadow(img, maxOpacity)

        # 障害物付与
        # 20%の確率で障害物を付与
        if random.random() < 0.2:
            levelOfOcclusion = random.uniform(0, 0.2)
            img = self.makeOcclusion(img, levelOfOcclusion)

        # 回転付与
        # 20%の確率で回転を付与
        if random.random() < 0.2:
            levelOfRotation = random.uniform(-10, 10)
            img = self.rotateImage(img, levelOfRotation)

        # 明るさ調整
        # 20%の確率で明るさを調整
        if random.random() < 0.2:
            levelOfBrightness = random.uniform(0.5, 1.3)
            img = self.changeBrightness(img, levelOfBrightness)

        # コントラスト調整
        # 20%の確率でコントラストを調整
        if random.random() < 0.2:
            levelOfContrast = random.uniform(0.5, 1.3)
            img = self.changeContrast(img, levelOfContrast)

        # 鮮やかさ調整
        # 20%の確率で鮮やかさを調整
        if random.random() < 0.2:
            levelOfSaturation = random.uniform(0.5, 1.3)
            img = self.changeSaturation(img, levelOfSaturation)

        # 振動付与
        # 20%の確率で振動を付与
        if random.random() < 0.2:
            levelOfVibration = random.randint(0, 5)
            img = self.makeVibration(img, levelOfVibration)

        # 解像度変更
        # 20%の確率で解像度を変更
        if random.random() < 0.2:
            levelOfResolutionChange = random.randint(0, 10)
            img = self.makeResolutionChange(img, levelOfResolutionChange)

        # 射影変換付与
        # 80%の確率で射影変換を付与
        if random.random() < 0.8:
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
        
            # YOLOラベルの射影変換後の座標に更新
            yoloLabels = self.transformYoloBbox(yoloLabels, perspective, self.NUMBER_PLATE_WIDTH, self.NUMBER_PLATE_HEIGHT)
        
        # 画像とラベルの保存
        if trainOrValid == "train":
            imagePath = f"{self.DATA_SET_OCR_DIR}/train/images/{fileName}.png"
            labelPath = f"{self.DATA_SET_OCR_DIR}/train/labels/{fileName}.txt"
        else:
            imagePath = f"{self.DATA_SET_OCR_DIR}/valid/images/{fileName}.png"
            labelPath = f"{self.DATA_SET_OCR_DIR}/valid/labels/{fileName}.txt"

        img.save(imagePath)
        with open(labelPath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(yoloLabels))

    def makeGaussianNoise(self, numberPlateImage, levelOfGaussianNoise):
        npImage = np.array(numberPlateImage)
        noise = np.random.normal(0, levelOfGaussianNoise, npImage.shape).astype('int16')
        noisyImgArray = npImage.astype('int16') + noise
        noisyImgArray = np.clip(noisyImgArray, 0, 255).astype('uint8')
        noisyImage = Image.fromarray(noisyImgArray)

        return noisyImage

    def makeBlur(self, numberPlateImage, levelOfBlur):
        if levelOfBlur == 0:
            return numberPlateImage
        blurredImage = numberPlateImage.filter(ImageFilter.GaussianBlur(radius=levelOfBlur))

        return blurredImage
    
    def makeMotionBlur(self, numberPlateImage, levelOfMotionBlur):
        if levelOfMotionBlur == 0:
            return numberPlateImage
        blurredImage = numberPlateImage.filter(ImageFilter.BoxBlur(radius=levelOfMotionBlur))

        return blurredImage
    
    def makePepperAndSaltNoise(self, numberPlateImage, levelOfPepperAndSaltNoise):
        if levelOfPepperAndSaltNoise == 0:

            return numberPlateImage

        npImage = np.array(numberPlateImage)
        saltVsPepper = 0.5
        amount = 0.004 * levelOfPepperAndSaltNoise

        saltNumber = np.ceil(amount * npImage.size * saltVsPepper)
        coordinates = [np.random.randint(0, i - 1, int(saltNumber)) for i in npImage.shape]
        npImage[coordinates[0], coordinates[1], :] = 255

        pepperNumber = np.ceil(amount * npImage.size * (1. - saltVsPepper))
        coordinates = [np.random.randint(0, i - 1, int(pepperNumber)) for i in npImage.shape]
        npImage[coordinates[0], coordinates[1], :] = 0

        return Image.fromarray(npImage)

    def makeSunGlare(self, numberPlateImage, maxRadiusRatio, levelOfSunGlare):
        npImage = np.array(numberPlateImage, dtype=np.float32)
        width, height = numberPlateImage.size
        
        center_x = random.randint(width // 4, width * 3 // 4)
        center_y = random.randint(height // 4, height * 3 // 4)
        
        radius = random.randint(int(width * maxRadiusRatio * 0.1), int(width * maxRadiusRatio))
        intensity = random.randint(50, levelOfSunGlare)
        
        for y in range(height):
            for x in range(width):
                distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                
                if distance < radius:
                    attenuation = np.exp(-0.5 * (distance / (radius / 3))**2)
                    
                    glare = intensity * attenuation
                    npImage[y, x, :] += glare
        
        npImage = np.clip(npImage, 0, 255).astype(np.uint8)
        return Image.fromarray(npImage)

    def makeRandomShadow(self, numberPlateImage, levelOfRandomShadow):
        npImage = np.array(numberPlateImage, dtype=np.int16)
        width, height = numberPlateImage.size
        
        corners = [
            (random.randint(-width//2, width*3//2), random.randint(-height//2, height*3//2))
            for _ in range(4)
        ]
        
        opacity = random.uniform(0.1, levelOfRandomShadow)
        
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.polygon(corners, fill=255)
        
        mask = mask.filter(ImageFilter.GaussianBlur(radius=random.randint(5, 15)))
        npMask = np.array(mask) / 255.0
        
        for c in range(3):
            npImage[:, :, c] = npImage[:, :, c] * (1 - npMask * opacity)
            
        npImage = np.clip(npImage, 0, 255).astype(np.uint8)
        return Image.fromarray(npImage)
    
    def makeVibration(self, numberPlateImage, levelOfVibration):
        npImage = np.array(numberPlateImage, dtype=np.int16)
        height, width = npImage.shape[:2]
        
        for y in range(height):
            for x in range(width):
                npImage[y, x] = npImage[y, x] + random.randint(-levelOfVibration, levelOfVibration)
        
        npImage = np.clip(npImage, 0, 255).astype(np.uint8)
        return Image.fromarray(npImage)

    def makeResolutionChange(self, numberPlateImage, levelOfResolutionChange):
        npImage = np.array(numberPlateImage, dtype=np.int16)
        height, width = npImage.shape[:2]
        
        for y in range(height):
            for x in range(width):
                npImage[y, x] = npImage[y, x] + random.randint(-levelOfResolutionChange, levelOfResolutionChange)
        
        npImage = np.clip(npImage, 0, 255).astype(np.uint8)
        return Image.fromarray(npImage)

    def makeOcclusion(self, numberPlateImage, levelOfOcclusion):
        npImage = np.array(numberPlateImage, dtype=np.int16)
        height, width = npImage.shape[:2]
    
        occlusionW = int(width * random.uniform(0.05, levelOfOcclusion))
        occlusionH = int(height * random.uniform(0.05, levelOfOcclusion))
    
        centerX = random.randint(0, width - occlusionW)
        centerY = random.randint(0, height - occlusionH)
    
        npImage[centerY:centerY + occlusionH, centerX:centerX + occlusionW] = 0
    
        occlusionImage = Image.fromarray(npImage.astype(np.uint8)) 
        
        return occlusionImage.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5)))

    def changeSaturation(self, numberPlateImage, levelOfSaturation):
        enhancer = ImageEnhance.Color(numberPlateImage)

        return enhancer.enhance(levelOfSaturation)
    
    def rotateImage(self, numberPlateImage, levelOfRotation):
        fillColorR = random.randint(0, 255)
        fillColorG = random.randint(0, 255)
        fillColorB = random.randint(0, 255)

        return numberPlateImage.rotate(levelOfRotation, expand=True, fillcolor=(fillColorR, fillColorG, fillColorB))

    def changeBrightness(self, numberPlateImage, levelOfBrightness):
        enhancer = ImageEnhance.Brightness(numberPlateImage)

        return enhancer.enhance(levelOfBrightness)
    
    def changeContrast(self, numberPlateImage, levelOfContrast):
        enhancer = ImageEnhance.Contrast(numberPlateImage)

        return enhancer.enhance(levelOfContrast)

    def makePerspectiveTransform(self, numberPlateImage, levelOfPerspectiveUp, levelOfPerspectiveDown, levelOfPerspectiveRight, levelOfPerspectiveLeft):
        width, height = numberPlateImage.size
        
        # 射影変換の最大オフセット計算
        maxRandomOffset = int(max(width, height) * 0.12)
        
        # 射影変換の各オフセット計算
        maxOffsetUp = int(abs(levelOfPerspectiveUp) / 45 * maxRandomOffset)
        maxOffsetDown = int(abs(levelOfPerspectiveDown) / 45 * maxRandomOffset)
        maxOffsetRight = int(abs(levelOfPerspectiveRight) / 45 * maxRandomOffset)
        maxOffsetLeft = int(abs(levelOfPerspectiveLeft) / 45 * maxRandomOffset)
        
        # 射影変換の最大オフセットが0ならば、射影変換しない
        if maxOffsetUp < 1 and maxOffsetDown < 1 and maxOffsetRight < 1 and maxOffsetLeft < 1:
            homographyMatrix = np.eye(3)
            return numberPlateImage, homographyMatrix

        topLeftXOffset = random.randint(-maxOffsetLeft, maxOffsetLeft)
        topLeftYOffset = random.randint(-maxOffsetUp, maxOffsetUp)
        
        topRightXOffset = random.randint(-maxOffsetRight, maxOffsetRight)
        topRightYOffset = random.randint(-maxOffsetUp, maxOffsetUp)

        bottomRightXOffset = random.randint(-maxOffsetRight, maxOffsetRight)
        bottomRightYOffset = random.randint(-maxOffsetDown, maxOffsetDown)

        bottomLeftXOffset = random.randint(-maxOffsetLeft, maxOffsetLeft)
        bottomLeftYOffset = random.randint(-maxOffsetDown, maxOffsetDown)
        
        # 射影変換の対象点
        sourcePointsAbs = [
            0, 0, 
            width, 0, 
            width, height, 
            0, height
        ]
        
        # 射影変換の目標点
        targetPointsAbs = [
            0 + topLeftXOffset, 0 + topLeftYOffset,
            width + topRightXOffset, 0 + topRightYOffset,
            width + bottomRightXOffset, height + bottomRightYOffset,
            0 + bottomLeftXOffset, height + bottomLeftYOffset
        ]

        # 射影変換の計算
        coeffs = self.calculatePerspectiveCoeffs(sourcePointsAbs, targetPointsAbs)
        
        fillColorR = random.randint(0, 255)
        fillColorG = random.randint(0, 255)
        fillColorB = random.randint(0, 255)
        fillcolor = (fillColorR, fillColorG, fillColorB)
        
        # 射影変換の適用
        try:
            transformedImage = numberPlateImage.transform(
                (width, height),
                Image.Resampling.PERSPECTIVE,
                data = coeffs,
                fillcolor=fillcolor
            )
        except AttributeError:
            transformedImage = numberPlateImage.transform(
                (width, height),
                Image.PERSPECTIVE,
                data = coeffs,
                fillcolor=fillcolor
            )
        
        # 逆行列の計算
        homographyInverseMatrix = np.array([
            [coeffs[0], coeffs[1], coeffs[2]],
            [coeffs[3], coeffs[4], coeffs[5]],
            [coeffs[6], coeffs[7], 1.0]
        ])
        homographyMatrix = np.linalg.inv(homographyInverseMatrix)
        
        return transformedImage, homographyMatrix

    def transformYoloBbox(self, yoloLabels, perspective, width, height):
        newYoloLabels = []
        
        for label in yoloLabels:
            parts = label.split()
            classId = parts[0]
            xCenter, yCenter, w, h = [float(p) for p in parts[1:]]
            
            xMinNorm = xCenter - w / 2
            yMinNorm = yCenter - h / 2
            xMaxNorm = xCenter + w / 2
            yMaxNorm = yCenter + h / 2

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
    
    def getYoloBboxFromAbsolute(self, xMin, yMin, xMax, yMax, width, height):
        xCenter = ((xMin + xMax) / 2) / width
        yCenter = ((yMin + yMax) / 2) / height

        w = (xMax - xMin) / width
        h = (yMax - yMin) / height
        
        return xCenter, yCenter, w, h