__package__ = "TEST"

from ultralytics import YOLO
import cv2
import os
import TRAIN
import re

class TEST:
    MODEL_TO_LOAD = None
    LAST_PT_PATH = None
    TEST_DIR = "./test"
    OUTPUT_DIR = TRAIN.TRAIN.OUTPUT_DIR
    MODEL_NAME = "yolo11n"
    NAME = "license_plate_11n"

    def __init__(self, confNumber, dataSetNumber):
        confNumber = float(confNumber) / 100.0
        dataSetNumber = int(dataSetNumber)

        if dataSetNumber == 0:
            self.NAME = f"{self.NAME}_detect"
            self.TEST_DIR = f"{self.TEST_DIR}_detect"
            self.OUTPUT_DIR = f"{self.OUTPUT_DIR}_detect"
        elif dataSetNumber == 1:
            self.NAME = f"{self.NAME}_ocr"
            self.TEST_DIR = f"{self.TEST_DIR}_ocr"
            self.OUTPUT_DIR = f"{self.OUTPUT_DIR}_ocr"

        try:
            if os.path.exists(self.OUTPUT_DIR):
                folderNames = os.listdir(self.OUTPUT_DIR)
                
                pattern = re.compile(rf'^({self.NAME})(\d+)$') 
                
                numbered_folders = []
                for name in folderNames:
                    match = pattern.match(name)
                    if match:
                        number = int(match.group(2))
                        numbered_folders.append((number, name))

                if numbered_folders:
                    latest_folder_name = max(numbered_folders)[1] 
                    
                    self.LAST_PT_PATH = os.path.join(
                        self.OUTPUT_DIR,
                        latest_folder_name,
                        "weights",
                        "best.pt"
                    )
                    
                    if os.path.exists(self.LAST_PT_PATH):
                        self.MODEL_TO_LOAD = self.LAST_PT_PATH
                    
                
                if self.MODEL_TO_LOAD:
                    self.MODEL = YOLO(self.MODEL_TO_LOAD)
                    print(f"前回の学習結果（{self.MODEL_TO_LOAD}）を読み込みました。")

                elif os.path.exists(os.path.join(self.OUTPUT_DIR, self.NAME, "weights", "best.pt")):
                    self.MODEL = YOLO(os.path.join(self.OUTPUT_DIR, self.NAME, "weights", "best.pt"))
                    print(f"前回の学習結果({self.NAME}/weights/best.pt)を読み込みました。")

                else:
                    print("ERROR: 学習結果がありません。学習を行ってください。")
                    return

            else:
                print("ERROR: 学習結果がありません。学習を行ってください。")
                return
                
        except OSError:
            raise RuntimeError("ERROR: モデルの読み込みに失敗しました。")
        except FileNotFoundError:
            raise RuntimeError("ERROR: モデルが見つかりません。")
        
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
