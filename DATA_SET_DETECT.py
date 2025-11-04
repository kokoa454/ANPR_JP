__package__ = "DATA_SET_DETECT"

import os
from roboflow import Roboflow
import shutil

# -- 位置検知用データセット生成クラス --
class DATA_SET_DETECT:
    API_KEY = None
    PROJECT_ID = None

    DATA_SET_DETECT_DIR = "./data_set_detect"

    def __init__(self, apiKey, projectId):
        self.API_KEY = apiKey
        self.PROJECT_ID = projectId

        if os.path.exists(self.DATA_SET_DETECT_DIR):
            print("\n前回の位置検知用データセットを削除します。")
            shutil.rmtree(self.DATA_SET_DETECT_DIR)
            print("前回の位置検知用データセットを削除しました。")

        print("位置検知用データセットをダウンロードします。")
        self.downloadDataSet(self.API_KEY, self.PROJECT_ID)
        print("位置検知用データセットをダウンロードしました。")

    def downloadDataSet(self, apiKey, projectId):
        # RoboflowのAPIキー設定
        try:
            rf = Roboflow(api_key = apiKey)
        except Exception:
            raise Exception("ERROR: APIキーが正しくありません。")

        # Roboflowのプロジェクト取得
        try:
            project = rf.workspace("questions").project(projectId)
        except Exception:
            raise Exception("ERROR: プロジェクトIDが正しくありません。")

        # データセットのダウンロード
        version = project.version(2)
        dataset = version.download("yolov11")

        # フォルダのリネーム
        if os.path.exists(dataset.location):
            try:
                os.rename(dataset.location, self.DATA_SET_DETECT_DIR)
                print(f"フォルダを{dataset.location}から{self.DATA_SET_DETECT_DIR}へリネームしました。")
            except Exception:
                raise Exception("ERROR: フォルダのリネーム中にエラーが発生しました。")

        return
