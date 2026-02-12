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
                trainingNumber = int(input("Epoch数? (デフォルト: 100): "))

                if trainingNumber == "":
                    trainingNumber = 100
                elif trainingNumber < 1:
                    print("1以上の数字を入力してください。\n")
                    continue
            except ValueError:
                print("数字を入力してください。\n")
                continue

            try:
                patience = int(input("Patience? (デフォルト: 10): "))

                if patience == "":
                    patience = 10
                elif patience < 1:
                    print("1以上の数字を入力してください。\n")
                    continue
            except ValueError:
                print("数字を入力してください。\n")
                continue

            try:
                batchSize = int(input("Batch Size? (デフォルト: 8): "))

                if batchSize == "":
                    batchSize = 16
                elif batchSize < 1:
                    print("1以上の数字を入力してください。\n")
                    continue
            except ValueError:
                print("数字を入力してください。\n")
                continue

            try:
                workers = int(input("Workers? (デフォルト: 4): "))

                if workers == "":
                    workers = 8
                elif workers < 1:
                    print("1以上の数字を入力してください。\n")
                    continue
            except ValueError:
                print("数字を入力してください。\n")
                continue

            try:
                cache = input("Cache? (デフォルト: True): ")

                if cache == "":
                    cache = True
                elif cache == "True" or cache == "true" :
                    cache = True
                elif cache == "False" or cache == "false":
                    cache = False
                else:
                    print("TrueかFalseを入力してください。\n")
                    continue
            except ValueError:
                print("TrueかFalseを入力してください。\n")
                continue

            TRAIN(
                dataSetNumber = dataSetNumber,
                trainingNumber= trainingNumber,
                patience = patience,
                batch_size = batchSize,
                workers = workers,
                cache = cache
            )
            print("\n")

        # -- テスト --
        elif selectedNum == 3:
            try:
                dataSetNumber = int(input("テストするデータセット番号? (0: 位置検知用 1: OCR用): "))

                if dataSetNumber not in [0, 1]:
                    print("0~1の数字を入力してください。\n")
                    continue

                if dataSetNumber == 0:
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

                    imgsz = input("ナンバープレート検出画像サイズ? (デフォルト: 1024): ")

                    if imgsz == "":
                        imgsz = 1024
                    else:
                        imgsz = int(imgsz)

                    if imgsz < 1:
                        print("1以上の数字を入力してください。\n")
                        continue

                    TEST_DETECT(confNumber, imgsz)
                elif dataSetNumber == 1:
                    try:
                        confNumberForDetect = int(input("ナンバープレート検出推論精度(%)?: "))

                        if confNumberForDetect < 1:
                            print("1以上の数字を入力してください。\n")
                            continue
                        elif confNumberForDetect > 100:
                            print("100以下の数字を入力してください。\n")
                            continue
                    except ValueError:
                        print("数字を入力してください。\n")
                        continue

                    try:
                        confNumberForOCR = int(input("OCR推論精度(%)?: "))

                        if confNumberForOCR < 1:
                            print("1以上の数字を入力してください。\n")
                            continue
                        elif confNumberForOCR > 100:
                            print("100以下の数字を入力してください。\n")
                            continue
                    except ValueError:
                        print("数字を入力してください。\n")
                        continue

                    imgszForDetect = input("ナンバープレート検出画像サイズ? (デフォルト: 1024): ")

                    if imgszForDetect == "":
                        imgszForDetect = 1024
                    else:
                        imgszForDetect = int(imgszForDetect)

                    if imgszForDetect < 1:
                        print("1以上の数字を入力してください。\n")
                        continue

                    imgszForOCR = input("OCR画像サイズ? (デフォルト: 1024): ")

                    if imgszForOCR == "":
                        imgszForOCR = 1024
                    else:
                        imgszForOCR = int(imgszForOCR)

                    if imgszForOCR < 1:
                        print("1以上の数字を入力してください。\n")
                        continue

                    TEST_OCR(confNumberForDetect, confNumberForOCR, imgszForDetect, imgszForOCR)
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

if __name__ == '__main__':
    main()
