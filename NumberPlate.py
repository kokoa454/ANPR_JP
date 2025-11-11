__package__ = "NumberPlate"

import re

# 車種別リスト
TYPE_OF_VEHICLE_LIST = ["普通_自家用", "普通_事業用", "軽_自家用", "軽_事業用"]

# 分類番号アルファベットリスト
ALPHABET_LIST = ["A", "C", "F", "H", "K", "L", "M", "P", "X", "Y"]

# 地名コード
REGION_CODE_LIST = [
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

# 全てのひらがなリスト
HIRAGANA_CODE_LIST_ALL = [
    "あ", "い", "う", "え",
    "か", "き", "く", "け", "こ",
    "さ", "す", "せ", "そ",
    "た", "ち", "つ", "て", "と",
    "な", "に", "ぬ", "ね", "の",
    "は", "ひ", "ふ", "へ", "ほ",
    "ま", "み", "む", "め", "も",
    "や", "ゆ", "よ",
    "ら", "り", "る", "れ", "ろ",
    "わ"
]

# 特殊文字リスト
SPECIAL_CHARACTER_LIST = ["・", "-"]

class NumberPlate:
    def __init__(self):
        self.typeOfVehicle = ""
        self.regionCode = ""
        self.classNum = ""
        self.hiraganaCode = ""
        self.registNum = ""

    def formatNPText(
            self,
            typeOfVehicle: str,
            upperRowText: str,
            lowerRowText: str
        ) -> str:
        if typeOfVehicle == "" or typeOfVehicle is None or typeOfVehicle not in TYPE_OF_VEHICLE_LIST:
            self.typeOfVehicle = "???"
        else:
            self.typeOfVehicle = typeOfVehicle

        for char in upperRowText:
            if char.isdigit() or char in ALPHABET_LIST:
                self.classNum += char
            else:
                self.regionCode += char

        for char in lowerRowText:
            if char.isdigit() or char in SPECIAL_CHARACTER_LIST:
                self.registNum += char
            else:
                self.hiraganaCode += char

        self.regionCode = "".join(self.regionCode)
        self.classNum = "".join(self.classNum)
        self.registNum = "".join(self.registNum)

        if self.regionCode == "" or self.regionCode not in REGION_CODE_LIST:
            self.regionCode = "???"

        if self.classNum == "" or len(self.classNum) < 2 or len(self.classNum) > 4:
            self.classNum = "???"

        if self.hiraganaCode == "" or self.hiraganaCode not in HIRAGANA_CODE_LIST_ALL:
            self.hiraganaCode = "?"

        if self.registNum == "" or (len(self.registNum) != 4 and len(self.registNum) != 5) or re.match(r'・\d{3}|・{2}\d{2}|・{3}\d{1}|\d{2}-\d{2}$', self.registNum) is None:
            self.registNum = "????"

        return f"{self.typeOfVehicle}\n{self.regionCode} {self.classNum} {self.hiraganaCode} {self.registNum}"
