__package__ = "TEST_OCR"

from ultralytics import YOLO
import cv2
import os
import TRAIN
import re

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

    def __init__(self, confNumber):
        confNumber = float(confNumber) / 100.0

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
                    print("ERROR: 位置検知モデルの学習結果がありません。学習を行ってください。")
                    return

            else:
                print("ERROR: 位置検知モデルの学習結果がありません。学習を行ってください。")
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
                    print("ERROR: OCRモデルの学習結果がありません。学習を行ってください。")
                    return

            else:
                print("ERROR: OCRモデルの学習結果がありません。学習を行ってください。")
                return
                
        except OSError:
            raise RuntimeError("ERROR: OCRモデルの読み込みに失敗しました。")
        except FileNotFoundError:
            raise RuntimeError("ERROR: OCRモデルが見つかりません。")
        

        #TODO : テスト画像の存在確認とテスト画像のコピーを作る
        try:
            if not os.path.exists(self.TEST_DIR):
                print("ERROR: テスト画像を追加してください。")
                os.makedirs(self.TEST_DIR)
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

            # TODO : 位置検知とOCRの実行部分の実装
            for file in os.listdir(self.TEST_DIR + "/test_images"):
                image = cv2.imread(os.path.join(self.TEST_DIR, "test_images", file))
                result = self.MODEL(
                    image,
                    conf = confNumber,
                    save = False
                )

                detections = result[0].boxes.xyxy
                licensePlateNumber = len(detections)

                cv2.putText(
                    image,
                    f"Number of License Plates: {str(licensePlateNumber)}",
                    (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.5,
                    (0, 255, 0),
                    2
                )

                for r in detections:
                    x1, y1, x2, y2 = map(int, r[:4])
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

                cv2.imwrite(
                    os.path.join(self.TEST_DIR + "/results_images", "result_" + file),
                    image
                )

        except OSError:
            raise RuntimeError("ERROR: テスト画像の読み込みに失敗しました。")
