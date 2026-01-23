from data_set_detect import DATA_SET_DETECT
from data_set_ocr import DATA_SET_OCR
from test_detect import TEST_DETECT
from test_ocr import TEST_OCR
from train import TRAIN

def main():
    print("【ANPR_JP】\n")
    
    while True:
        print("""\n作業番号 (
        0: 位置検知用データセット生成
        1: OCR用データセット生成
        2: 学習
        3: テスト
        4: 終了
        )\n""")

        # -- 作業番号入力 --
        try:
            selectedNum = int(input("作業番号?: "))
            
            if selectedNum not in [0, 1, 2, 3, 4]:
                print("0~4の数字を入力してください。\n")
                continue
        except ValueError:
            print("数字を入力してください。\n")
            continue

        print("\n")

        # -- 検知用データセット生成 --
        if selectedNum == 0:
            try:
                apiKey = input("RoboflowのAPIキー?: ")

                if apiKey == "":
                    print("APIキーを入力してください。\n")
                    continue
            except Exception:
                print("APIキーを入力してください。\n")
                continue

            try:
                projectAuthorId = input("Roboflowのプロジェクト作者ID?: ")

                if projectAuthorId == "":
                    print("プロジェクト作者IDを入力してください。\n")
                    continue
            except Exception:
                print("プロジェクト作者IDを入力してください。\n")
                continue

            try:
                projectId = input("RoboflowのプロジェクトID?: ")

                if projectId == "":
                    print("プロジェクトIDを入力してください。\n")
                    continue
            except Exception:
                print("プロジェクトIDを入力してください。\n")
                continue
                    
            DATA_SET_DETECT(apiKey, projectAuthorId, projectId)
            print("\n")

        # -- OCR用データセット生成 --
        elif selectedNum == 1:
            try:
                trainingNumber = int(input("ナンバープレート数?: "))

                if trainingNumber < 1:
                    print("1以上の数字を入力してください。\n")
                    continue
            except ValueError:
                print("数字を入力してください。\n")
                continue

            DATA_SET_OCR(trainingNumber)
            print("\n")
        
        # -- 学習 --
        elif selectedNum == 2:
            try:
                dataSetNumber = int(input("学習するデータセット番号? (0: 位置検知用 1: OCR用): "))

                if dataSetNumber not in [0, 1]:
                    print("0~1の数字を入力してください。\n")
                    continue
            except ValueError:
                print("数字を入力してください。\n")
                continue

            try:
                trainingNumber = int(input("Epoch数?: "))

                if trainingNumber < 1:
                    print("1以上の数字を入力してください。\n")
                    continue
            except ValueError:
                print("数字を入力してください。\n")
                continue

            batchSize = input("バッチサイズ? (デフォルト: 8): ")

            if batchSize == "":
                batchSize = 8

            batchSize = int(batchSize)

            if batchSize < 1:
                print("1以上の数字を入力してください。\n")
                continue

            patience = input("Patience? (デフォルト: 20): ")

            if patience == "":
                patience = 20

            patience = int(patience)

            if patience < 1:
                print("1以上の数字を入力してください。\n")
                continue

            optimizer = input("オプティマイザ? (デフォルト: AdamW): ")

            if optimizer == "":
                optimizer = "AdamW"

            learning_rate = input("学習率? (デフォルト: 0.001): ")

            if learning_rate == "":
                learning_rate = 0.001

            learning_rate = float(learning_rate)

            if learning_rate <= 0:
                print("0より大きい数字を入力してください。\n")
                continue

            cos_lr_input = input("コサイン変化学習率? (True / False) (デフォルト: True): ")

            if cos_lr_input == "":
                cos_lr = True
            elif cos_lr_input == "True" or cos_lr_input == "true" :
                cos_lr = True
            elif cos_lr_input == "False" or cos_lr_input == "false":
                cos_lr = False
            else:
                print("TrueかFalseを入力してください。\n")
                continue

            hsv_s = input("HSV S値? (デフォルト: 0.7): ")

            if hsv_s == "":
                hsv_s = 0.7

            hsv_s = float(hsv_s)

            if hsv_s < 0:
                print("0以上の数字を入力してください。\n")
                continue

            hsv_v = input("HSV V値? (デフォルト: 0.4): ")

            if hsv_v == "":
                hsv_v = 0.4

            hsv_v = float(hsv_v)

            if hsv_v < 0:
                print("0以上の数字を入力してください。\n")
                continue

            imgsz = input("画像サイズ? (デフォルト: 1024): ")

            if imgsz == "":
                imgsz = 1024

            imgsz = int(imgsz)

            if imgsz < 1:
                print("1以上の数字を入力してください。\n")
                continue

            iou = input("IoU? (デフォルト: 0.6): ")

            if iou == "":
                iou = 0.6

            iou = float(iou)

            if iou < 0 or iou > 1:
                print("0以上1以下の数字を入力してください。\n")
                continue

            augment = input("Augment? (True / False) (デフォルト: True): ")

            if augment == "":
                augment = True
            elif augment == "True" or augment == "true" :
                augment = True
            elif augment == "False" or augment == "false":
                augment = False
            else:
                print("TrueかFalseを入力してください。\n")
                continue

            if dataSetNumber == 0:
                mosaic = input("Mosaic? (True / False) (デフォルト: True): ")

                if mosaic == "":
                    mosaic = True
                elif mosaic == "True" or mosaic == "true" :
                    mosaic = True
                elif mosaic == "False" or mosaic == "false":
                    mosaic = False
                else:
                    print("TrueかFalseを入力してください。\n")
                    continue

                scale = input("Scale? (デフォルト: 0.5): ")

                if scale == "":
                    scale = 0.5

                scale = float(scale)

                if scale < 0 or scale > 1:
                    print("0以上1以下の数字を入力してください。\n")
                    continue

                translate = input("Translate? (デフォルト: 0.1): ")

                if translate == "":
                    translate = 0.1

                translate = float(translate)

                if translate < 0 or translate > 1:
                    print("0以上1以下の数字を入力してください。\n")
                    continue

                fliplr = input("Fliplr? (デフォルト: 0.5): ")

                if fliplr == "":
                    fliplr = 0.5

                fliplr = float(fliplr)

                if fliplr < 0 or fliplr > 1:
                    print("TrueかFalseを入力してください。\n")
                    continue

                close_mosaic = input("Close Mosaic? (デフォルト: 10): ")

                if close_mosaic == "":
                    close_mosaic = 10
                else:
                    close_mosaic = int(close_mosaic)

                if close_mosaic < 0:
                    print("0以上の数字を入力してください。\n")
                    continue

                retina_masks = input("Retina Masks? (True / False) (デフォルト: True): ")

                if retina_masks == "":
                    retina_masks = True
                elif retina_masks == "True" or retina_masks == "true" :
                    retina_masks = True
                elif retina_masks == "False" or retina_masks == "false":
                    retina_masks = False
                else:
                    print("TrueかFalseを入力してください。\n")
                    continue

            else:
                mosaic = input("Mosaic? (True / False) (デフォルト: False): ")

                if mosaic == "":
                    mosaic = False
                elif mosaic == "True" or mosaic == "true" :
                    mosaic = True
                elif mosaic == "False" or mosaic == "false":
                    mosaic = False
                else:
                    print("TrueかFalseを入力してください。\n")
                    continue

                scale = input("Scale? (デフォルト: 0.2): ")

                if scale == "":
                    scale = 0.2

                scale = float(scale)

                if scale < 0 or scale > 1:
                    print("0以上1以下の数字を入力してください。\n")
                    continue

                translate = input("Translate? (デフォルト: 0.05): ")

                if translate == "":
                    translate = 0.05

                translate = float(translate)

                if translate < 0 or translate > 1:
                    print("0以上1以下の数字を入力してください。\n")
                    continue

                fliplr = input("Fliplr? (デフォルト: 0): ")

                if fliplr == "":
                    fliplr = 0

                fliplr = float(fliplr)

                if fliplr < 0 or fliplr > 1:
                    print("TrueかFalseを入力してください。\n")
                    continue

                close_mosaic = input("Close Mosaic? (デフォルト: 10): ")

                if close_mosaic == "":
                    close_mosaic = 10
                else:
                    close_mosaic = int(close_mosaic)

                if close_mosaic < 0:
                    print("0以上の数字を入力してください。\n")
                    continue

                retina_masks = input("Retina Masks? (デフォルト: False): ")

                if retina_masks == "":
                    retina_masks = False
                elif retina_masks == "True" or retina_masks == "true" :
                    retina_masks = True
                elif retina_masks == "False" or retina_masks == "false":
                    retina_masks = False
                else:
                    print("TrueかFalseを入力してください。\n")
                    continue


            TRAIN(
                dataSetNumber = dataSetNumber,
                trainingNumber= trainingNumber,
                patience = patience,
                batch_size = batchSize,
                optimizer = optimizer,
                learning_rate = learning_rate,
                cos_lr = cos_lr,
                hsv_s = hsv_s,
                hsv_v = hsv_v,
                imgsz = imgsz,
                mosaic = mosaic,
                scale = scale,
                translate = translate,
                augment = augment,
                fliplr = fliplr,
                close_mosaic = close_mosaic,
                iou = iou,
                retina_masks = retina_masks
            )
            print("\n")

        # -- テスト --
        elif selectedNum == 3:
            try:
                confNumber = int(input("推論精度(%)?: "))

                if confNumber < 1:
                    print("1以上の数字を入力してください。\n")
                    continue
                elif confNumber > 100:
                    print("100以下の数字を入力してください。\n")
                    continue
            except ValueError:
                print("数字を入力してください。\n")
                continue

            try:
                dataSetNumber = int(input("テストするデータセット番号? (0: 位置検知用 1: OCR用): "))

                if dataSetNumber not in [0, 1]:
                    print("0~1の数字を入力してください。\n")
                    continue

                else:
                    imgsz = input("画像サイズ? (デフォルト: 1024): ")

                    if imgsz == "":
                        imgsz = 1024
                    else:
                        imgsz = int(imgsz)

                    if imgsz < 1:
                        print("1以上の数字を入力してください。\n")
                        continue

                    if dataSetNumber == 0:
                        TEST_DETECT(confNumber, imgsz)
                    elif dataSetNumber == 1:
                        TEST_OCR(confNumber, imgsz)
            except ValueError:
                print("数字を入力してください。\n")
                continue

            print("\n")

        # -- 終了 --
        elif selectedNum == 4:
            break
    
        # -- 入力エラー --
        else:
            print("0~4の数字を入力してください。\n")

main()
