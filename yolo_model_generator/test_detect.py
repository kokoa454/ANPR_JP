from ultralytics import YOLO
import cv2
import os
from train import TRAIN
import re

# -- 位置検知用テストクラス --
class TEST_DETECT:
    MODEL_TO_LOAD = None
    LAST_PT_PATH = None
    TEST_DIR = "./test_detect"
    OUTPUT_DIR = f"{TRAIN.OUTPUT_DIR}_detect"
    MODEL_NAME = "yolo11m-seg"
    NAME = "number_plate_11m_detect"
    MODEL = None

    def __init__(self, confNumber):
        confNumber = float(confNumber) / 100.0

        self.loadModel()
        self.runTest(confNumber)
        
    def loadModel(self):
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
        
    def runTest(self, confNumber):
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

            # 推論実行開始
            for file in os.listdir(self.TEST_DIR + "/test_images"):
                image = cv2.imread(os.path.join(self.TEST_DIR, "test_images", file))
                overlay = image.copy()
                
                # 推論結果取得
                result = self.MODEL(
                    image,
                    conf = confNumber,
                    save = False
                )

                detections = result[0].boxes.xyxy
                numberPlateNumber = len(detections)
                masks = result[0].masks

                # 推論結果のセグメンテーションマスク描画
                if masks is not None:
                    segmentMasks = masks.data.cpu().numpy()
                    
                    for i, mask in enumerate(segmentMasks):
                        resizedMask = cv2.resize(
                            mask,
                            (image.shape[1], image.shape[0]),
                            interpolation=cv2.INTER_NEAREST
                        )

                        maskBoolean = resizedMask > 0.5
                        color = (0, 255, 0)

                        for channel in range(3):
                            overlay[:, :, channel][maskBoolean] = (
                                0.5 * overlay[:, :, channel][maskBoolean] + 0.5 * color[channel]
                            )
                        
                        boundingBox = detections[i]
                        x1, y1, x2, y2 = map(int, boundingBox)
                        cv2.rectangle(
                            overlay,
                            (x1, y1),
                            (x2, y2),
                            (255, 0, 0),
                            2
                        )
                
                finalImage = cv2.addWeighted(overlay, 0.7, image, 0.3, 0)
                
                cv2.putText(
                    finalImage,
                    f"Number of Number Plates: {str(numberPlateNumber)}",
                    (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.5,
                    (0, 255, 0),
                    2
                )

                cv2.imwrite(
                    os.path.join(self.TEST_DIR + "/results_images", "result_" + file),
                    finalImage
                )

        except OSError:
            raise RuntimeError("ERROR: テスト画像の読み込みに失敗しました。")