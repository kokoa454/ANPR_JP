import os
import re
import torch
from ultralytics import YOLO
from data_set_detect import DATA_SET_DETECT
from data_set_ocr import DATA_SET_OCR

# -- 学習用クラス --
class TRAIN:
    OUTPUT_DIR = "./yolo_output"
    MODEL_TO_LOAD = None
    LAST_PT_PATH = None
    MODEL_NAME = "yolo11m"
    DATA_DETECT_PATH = f"{DATA_SET_DETECT.DATA_SET_DETECT_DIR}/data.yaml"
    DATA_OCR_PATH = f"{DATA_SET_OCR.DATA_SET_OCR_DIR}/data.yaml"
    DATA_PATH = None
    NAME = "number_plate_11m"
    PROJECT_PATH = "yolo_output"

    def __init__(
        self, 
        dataSetNumber, 
        trainingNumber, 
        patience, 
        batch_size, 
        optimizer, 
        learning_rate, 
        cos_lr, 
        hsv_s, 
        hsv_v, 
        imgsz,
        mosaic,
        scale,
        translate,
        augment,
        fliplr,
        close_mosaic,
        iou,
    ):
        dataSetNumber = int(dataSetNumber)

        if dataSetNumber == 0:
            if os.path.exists(self.DATA_DETECT_PATH):
                self.DATA_PATH = self.DATA_DETECT_PATH
                self.OUTPUT_DIR = f"{self.OUTPUT_DIR}_detect"
                self.NAME = f"{self.NAME}_detect"
                self.PROJECT_PATH = f"{self.PROJECT_PATH}_detect"
                self.MODEL_NAME = "yolo11m-seg"
            else:
                raise Exception("ERROR: 検知用データセットがありません。")

        elif dataSetNumber == 1:
            if os.path.exists(self.DATA_OCR_PATH):
                self.DATA_PATH = self.DATA_OCR_PATH
                self.OUTPUT_DIR = f"{self.OUTPUT_DIR}_ocr"
                self.NAME = f"{self.NAME}_ocr"
                self.PROJECT_PATH = f"{self.PROJECT_PATH}_ocr"
            else:
                raise Exception("ERROR: OCR用データセットがありません。")

        trainingNumber = int(trainingNumber)
        print(f"{self.MODEL_NAME}による学習を開始します。(Epochs: {trainingNumber}, Batch Size: {batch_size}, Image Size: {imgsz}, Optimizer: {optimizer}, Learning Rate: {learning_rate}, Cosine LR: {cos_lr}, HSV S: {hsv_s}, HSV V: {hsv_v}, Patience: {patience}, Mosaic: {mosaic}, Scale: {scale}, Translate: {translate}, Augment: {augment}, Fliplr: {fliplr}, Close Mosaic: {close_mosaic}, IoU: {iou}, Name: {self.NAME})")

        if not os.path.exists(self.PROJECT_PATH):
            os.makedirs(self.PROJECT_PATH)

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
                    self.MODEL = YOLO(f"{self.MODEL_NAME}.pt")
                    print(f"既存の重みが見つからなかったため、{self.MODEL_NAME}.pt で新規に学習します。")

            else:
                self.MODEL = YOLO(f"{self.MODEL_NAME}.pt")
                print(f"新規に学習します。")
                
        except OSError:
            raise RuntimeError("ERROR: モデルの読み込みに失敗しました。")
        except FileNotFoundError:
            raise RuntimeError("ERROR: モデルが見つかりません。")

        # 学習の実行
        try:
            if(torch.cuda.is_available()): # ultralyticsをインストール後、pytorchがcpu版の場合、pytorchだけを一度消し、pytorchだけを新たに再インストール(cuda13.0だったらcu130)を行う必要がある
                device = 0
                print("GPUで学習を始めます。")
            else:
                device = "cpu"
                print("CPUで学習を始めます。")
            results = self.MODEL.train(
                    data = self.DATA_PATH,
                    epochs = trainingNumber,
                    patience = patience,
                    batch = batch_size,
                    imgsz = imgsz,
                    name = self.NAME,
                    project = self.PROJECT_PATH,
                    workers = 0,
                    device = device,
                    cache = True,
                    optimizer = optimizer,
                    lr0 = learning_rate,
                    cos_lr = cos_lr,
                    hsv_s = hsv_s,
                    hsv_v = hsv_v,
                    mosaic = mosaic,
                    scale = scale,
                    translate = translate,
                    augment = augment,
                    fliplr = fliplr,
                    close_mosaic = close_mosaic,
                    iou = iou,
                )
        except RuntimeError:
            raise RuntimeError("ERROR: 学習に失敗しました。")

        print("学習を終了しました。")