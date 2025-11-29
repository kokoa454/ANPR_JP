from PIL import Image
import Models.Utilities as Utilities
import cv2
import numpy as np
from ultralytics import YOLO
import config.config as config

class NumberPlateRecognizer:
    def __init__(self):
        self.model = YOLO(model = config.DETECTION_MODEL)
        self.utilities = Utilities.Utilities()

    def detectNP(self, image: Image.Image) -> Image.Image | None:
        # yolo11n-seg-anpr-jp-detect.ptを使用してナンバープレートを検出
        detectionResults = self.model(
            source = image,
            imgsz = config.DETECTION_IMG_SIZE,
            conf = config.DETECTION_CONFIDENCE,
            iou = config.DETECTION_IOU,
            save = config.DETECTION_SAVE
        )

        # ナンバープレートの検出結果とマスクとナンバープレートの数を取得
        detections = detectionResults[0].boxes.xyxy
        masks = detectionResults[0].masks
        npNumber = len(detections)

        # ナンバープレートが検出された場合の処理
        if masks is not None and npNumber > 0:
            # マスクデータを取得
            segmentationMasks = masks.data.cpu().numpy()

            # ナンバープレートのマスクをリサイズして二値化
            resizedMask = self._createBinaryMask(segmentationMasks[0], np.array(image))

            # 凸包を検出して射影変換のための座標を取得
            hull = self._detectConvexHull(resizedMask)

            # 凸包が検出された場合、最も大きな凸包を取得して射影変換の座標を計算
            if hull:
                mainHull = max(hull, key=cv2.contourArea)
                rectangle = cv2.minAreaRect(mainHull)
                boxPoints = cv2.boxPoints(rectangle)
                sourcePoints = np.float32(boxPoints)
                sourcePoints = self._sortSourcePoints(sourcePoints)
                        
                if sourcePoints is not None:
                    # 画像をNumPy配列に変換
                    npImage = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                    # 射影変換を実行
                    npImage = self._transformPerspective(npImage, sourcePoints)

                    return Image.fromarray(cv2.cvtColor(npImage, cv2.COLOR_BGR2RGB))

        return None

    def _createBinaryMask(self, mask: np.ndarray, image: np.ndarray) -> np.ndarray:
        resizedMask = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
        maskBoolean = resizedMask > 0.5
        binaryMask = (maskBoolean * 255).astype('uint8')
        binaryMask = cv2.medianBlur(binaryMask, 5)
        binaryMask = cv2.morphologyEx(binaryMask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        return binaryMask

    def _detectConvexHull(self, mask: np.ndarray) -> np.ndarray:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def _sortSourcePoints(self, points: np.ndarray) -> np.ndarray:
        points = sorted(points, key=lambda x: (x[1], x[0]))
        top = sorted(points[:2], key=lambda x: x[0])
        bottom = sorted(points[2:], key=lambda x: x[0], reverse=True)
        return np.array(
            [
                top[0], 
                top[1], 
                bottom[0], 
                bottom[1]
            ], 
            dtype = "float32"
        )

    def _transformPerspective(self, image: np.ndarray, sourcePoints: np.ndarray) -> Image:
        TARGET_WIDTH = 440 * 2
        TARGET_HEIGHT = 220 * 2

        destination = np.array(
            [
                [0, 0], 
                [TARGET_WIDTH - 1, 0],
                [TARGET_WIDTH - 1, TARGET_HEIGHT - 1],
                [0, TARGET_HEIGHT - 1]
            ], 
            dtype = "float32"
        )

        homographyMatrix, _ = cv2.findHomography(sourcePoints, destination, cv2.RANSAC, 5.0)

        warpedPerspective = cv2.warpPerspective(image, homographyMatrix, (TARGET_WIDTH, TARGET_HEIGHT), cv2.INTER_CUBIC)

        fileName = f"{config.OUTPUT_DETECT_DIR}/detected_image_{self.utilities.getTimeStamp()}.png"
        cv2.imwrite(fileName, warpedPerspective)

        finalImage = cv2.cvtColor(src = warpedPerspective, code = cv2.COLOR_BGR2RGB)
        return finalImage
