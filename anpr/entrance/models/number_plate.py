import re
import config.config as config
import config.constance as constance

class NumberPlate:
    def __init__(self):
        self.region_code = config.UNDEFINED_TEXT
        self.class_num = config.UNDEFINED_TEXT
        self.hiragana_code = config.UNDEFINED_TEXT
        self.regist_num = config.UNDEFINED_TEXT

    def get_type_of_vehicle(self) -> str:
        return self.type_of_vehicle

    def get_region_code(self) -> str:
        return self.region_code

    def get_class_num(self) -> str:
        return self.class_num

    def get_hiragana_code(self) -> str:
        return self.hiragana_code

    def get_regist_num(self) -> str:
        return self.regist_num

    def format_number_plate_text(self, upper_row_text: str, lower_row_text: str) -> None:
        self.region_code = ""
        self.class_num = ""
        self.hiragana_code = ""
        self.regist_num = ""

        for char in upper_row_text:
            if char.isdigit() or char in constance.ALPHABET_LIST:
                self.class_num += char
            else:
                self.region_code += char

        for char in lower_row_text:
            if char.isdigit() or char in constance.SPECIAL_CHARACTER_LIST:
                self.regist_num += char
            else:
                self.hiragana_code += char

        if self.region_code == "" or self.region_code not in constance.REGION_CODE_LIST:
            self.region_code = config.UNDEFINED_TEXT

        if self.class_num == "" or len(self.class_num) < 2 or len(self.class_num) > 4:
            self.class_num = config.UNDEFINED_TEXT

        if self.hiragana_code == "" or self.hiragana_code not in constance.HIRAGANA_CODE_LIST_ALL:
            self.hiragana_code = config.UNDEFINED_TEXT

        if self.regist_num == "" or (len(self.regist_num) != 4 and len(self.regist_num) != 5) or re.match(r'・\d{3}|・{2}\d{2}|・{3}\d{1}|\d{2}-\d{2}$', self.regist_num) is None:
            self.regist_num = config.UNDEFINED_TEXT

        return None
