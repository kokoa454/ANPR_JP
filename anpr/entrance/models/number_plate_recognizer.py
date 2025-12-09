from PIL import Image
from models.utilities import Utilities
import cv2
import numpy as np
from ultralytics import YOLO
import config.config as config

class NumberPlateRecognizer:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self.model = YOLO(model = config.DETECTION_MODEL)

    def detect_number_plate(self, image: Image.Image) -> Image.Image | None:
        # yolo11n-seg-anpr-jp-detect.ptを使用してナンバープレートを検出
        detection_result = self.model(
            source = image,
            imgsz = config.DETECTION_IMG_SIZE,
            conf = config.DETECTION_CONFIDENCE,
            iou = config.DETECTION_IOU,
            save = config.DETECTION_SAVE
        )

        # ナンバープレートの検出結果とマスクとナンバープレートの数を取得
        detections = detection_result[0].boxes.xyxy
        masks = detection_result[0].masks
        number_plate_number = len(detections)

        # ナンバープレートが検出された場合の処理
        if masks is not None and number_plate_number > 0:
            # マスクデータを取得
            segmentation_masks = masks.data.cpu().numpy()

            # ナンバープレートのマスクをリサイズして二値化
            resized_mask = self._create_binary_mask(segmentation_masks[0], np.array(image))

            # 凸包を検出して射影変換のための座標を取得
            hull = self._detect_convex_hull(resized_mask)

            # this part was used for minAreaRect 
            # # 凸包が検出された場合、最も大きな凸包を取得して射影変換の座標を計算
            # if hull:
            #     main_hull = max(hull, key=cv2.contourArea)
            #     rectangle = cv2.minAreaRect(main_hull)
            #     box_points = cv2.boxPoints(rectangle)
            #     source_points = np.float32(box_points)
            #     source_points = self._sort_source_points(source_points)
                        
            #     if source_points is not None:
            #         # 画像をNumPy配列に変換
            #         np_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            #         # 射影変換を実行
            #         np_image = self._transform_perspective(np_image, source_points)

            #         return Image.fromarray(cv2.cvtColor(np_image, cv2.COLOR_BGR2RGB))
            
            if hull:
                main_hull = max(hull, key=cv2.contourArea)
                perimeter = cv2.arcLength(main_hull, True)
                epsilon = 0.02 * perimeter
                approx = cv2.approxPolyDP(main_hull, epsilon, True)
                
                if approx.shape[0] == 4:
                    source_points = np.float32(approx.reshape(4, 2))
                    source_points = self._sort_source_points(source_points)
                    
                    if source_points is not None:
                        np_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                        np_image = self._transform_perspective(np_image, source_points)

                        file_name = f"{config.OUTPUT_DETECT_DIR}/{Utilities.get_timestamp_for_local()}.png"
                        cv2.imwrite(file_name, np_image)
                        
                        return Image.fromarray(cv2.cvtColor(np_image, cv2.COLOR_BGR2RGB))
                    
        return None

    # this function was used for minAreaRect
    # def _create_binary_mask(self, mask: np.ndarray, image: np.ndarray) -> np.ndarray:
    #     resized_mask = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
    #     mask_boolean = resized_mask > 0.5
    #     binary_mask = (mask_boolean * 255).astype('uint8')
    #     binary_mask = cv2.medianBlur(binary_mask, 5)
    #     binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    #     return binary_mask

    def _create_binary_mask(self, mask: np.ndarray, image: np.ndarray) -> np.ndarray:
        resized_mask = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
        mask_boolean = resized_mask > 0.5
        binary_mask = (mask_boolean * 255).astype('uint8')
        binary_mask = cv2.medianBlur(binary_mask, 7)
        kernel = np.ones((7, 7), np.uint8)
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)
        
        return binary_mask

    def _detect_convex_hull(self, mask: np.ndarray) -> np.ndarray:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def _sort_source_points(self, points: np.ndarray) -> np.ndarray:
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

    def _transform_perspective(self, image: np.ndarray, source_points: np.ndarray) -> Image:
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

        homography_matrix, _ = cv2.findHomography(source_points, destination, cv2.RANSAC, 5.0)

        warped_perspective = cv2.warpPerspective(image, homography_matrix, (TARGET_WIDTH, TARGET_HEIGHT), cv2.INTER_CUBIC)

        final_image = cv2.cvtColor(src = warped_perspective, code = cv2.COLOR_BGR2RGB)
        return final_image