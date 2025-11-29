import re
import config.config as config
import config.constance as constance

class NumberPlate:
    def __init__(self):
        self.typeOfVehicle = config.UNDEFINED_TEXT
        self.regionCode = config.UNDEFINED_TEXT
        self.classNum = config.UNDEFINED_TEXT
        self.hiraganaCode = config.UNDEFINED_TEXT
        self.registNum = config.UNDEFINED_TEXT
        self.undefinedText = config.UNDEFINED_TEXT 

    def getTypeOfVehicle(self) -> str:
        return self.typeOfVehicle

    def getRegionCode(self) -> str:
        return self.regionCode

    def getClassNum(self) -> str:
        return self.classNum

    def getHiraganaCode(self) -> str:
        return self.hiraganaCode

    def getRegistNum(self) -> str:
        return self.registNum

    def formatNPText(self, typeOfVehicle: str, upperRowText: str, lowerRowText: str) -> None:
        if typeOfVehicle == "" or typeOfVehicle is None or typeOfVehicle not in constance.TYPE_OF_VEHICLE_LIST:
            self.typeOfVehicle = self.undefinedText
        else:
            self.typeOfVehicle = typeOfVehicle

        for char in upperRowText:
            if char.isdigit() or char in constance.ALPHABET_LIST:
                self.classNum += char
            else:
                self.regionCode += char

        for char in lowerRowText:
            if char.isdigit() or char in constance.SPECIAL_CHARACTER_LIST:
                self.registNum += char
            else:
                self.hiraganaCode += char

        if self.regionCode == "" or self.regionCode not in constance.REGION_CODE_LIST:
            self.regionCode = self.undefinedText

        if self.classNum == "" or len(self.classNum) < 2 or len(self.classNum) > 4:
            self.classNum = self.undefinedText

        if self.hiraganaCode == "" or self.hiraganaCode not in constance.HIRAGANA_CODE_LIST_ALL:
            self.hiraganaCode = self.undefinedText

        if self.registNum == "" or (len(self.registNum) != 4 and len(self.registNum) != 5) or re.match(r'・\d{3}|・{2}\d{2}|・{3}\d{1}|\d{2}-\d{2}$', self.registNum) is None:
            self.registNum = self.undefinedText

        return None
