import DATA_SET_OCR 
import DATA_SET_DETECT
import TRAIN
import TEST_DETECT
import TEST_OCR

def generateYoloModel():
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
                projectId = input("RoboflowのプロジェクトID?: ")

                if projectId == "":
                    print("プロジェクトIDを入力してください。\n")
                    continue
            except Exception:
                print("プロジェクトIDを入力してください。\n")
                continue
                    
            DATA_SET_DETECT.DATA_SET_DETECT(apiKey, projectId)
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

            DATA_SET_OCR.DATA_SET_OCR(trainingNumber)
            print("\n")
        
        # -- 学習 --
        elif selectedNum == 2:
            try:
                trainingNumber = int(input("Epoch数?: "))

                if trainingNumber < 1:
                    print("1以上の数字を入力してください。\n")
                    continue
            except ValueError:
                print("数字を入力してください。\n")
                continue

            try:
                print(
                    """\n学習するデータセット番号 (
                    0: 位置検知用
                    1: OCR用
                    )\n"""
                )
                dataSetNumber = int(input("学習するデータセット番号?: "))

                if dataSetNumber not in [0, 1]:
                    print("0~1の数字を入力してください。\n")
                    continue
            except ValueError:
                print("数字を入力してください。\n")
                continue

            TRAIN.TRAIN(dataSetNumber, trainingNumber)
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
                print(
                    """\nテストするデータセット番号 (
                    0: 位置検知用
                    1: OCR用
                    )\n"""
                )
                dataSetNumber = int(input("テストするデータセット番号?: "))

                if dataSetNumber not in [0, 1]:
                    print("0~1の数字を入力してください。\n")
                    continue
                elif dataSetNumber == 0:
                    TEST_DETECT.TEST_DETECT(confNumber)
                elif dataSetNumber == 1:
                    TEST_OCR.TEST_OCR(confNumber)
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

generateYoloModel()
