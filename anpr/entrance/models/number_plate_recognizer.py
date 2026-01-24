import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
import config.config as config
from models.utilities import Utilities

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
            
            if hull:
                # 最大の凸包を取得
                main_hull = max(hull, key=cv2.contourArea)
                perimeter = cv2.arcLength(main_hull, True)
                epsilon = 0.02 * perimeter
                
                # 凸包を多角形に近似
                approx = cv2.approxPolyDP(main_hull, epsilon, True)
                
                # 射影変換のための座標を取得
                if approx.shape[0] == 4:
                    source_points = np.float32(approx.reshape(4, 2))
                    source_points = self._sort_source_points(source_points)
                else:
                    rectangle = cv2.minAreaRect(main_hull)
                    box = cv2.boxPoints(rectangle)
                    source_points = np.float32(box)
                    source_points = self._sort_source_points(source_points)
                
                if source_points is not None:
                    # 射影変換
                    np_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                    np_image = self._transform_perspective(np_image, source_points)

                    file_name = f"{config.OUTPUT_DETECT_DIR}/{Utilities.get_timestamp()}.png"

                    # アンシャープマスキング
                    np_image = self._unsharp_masking(np_image)

                    # バイラテラルフィルタ
                    np_image = self._bilateral_filter(np_image)

                    # ディテールエンハンス
                    np_image = self._detail_enhance(np_image)

                    # ノイズ除去
                    np_image = self._noise_removal(np_image)

                    cv2.imwrite(file_name, np_image)
                    
                    return Image.fromarray(cv2.cvtColor(np_image, cv2.COLOR_BGR2RGB))
                    
        return None

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
        target_width = config.OCR_IMG_SIZE
        target_height = int(config.OCR_IMG_SIZE / 2)

        destination = np.array(
            [
                [0, 0], 
                [target_width - 1, 0],
                [target_width - 1, target_height - 1],
                [0, target_height - 1]
            ], 
            dtype = "float32"
        )

        homography_matrix, _ = cv2.findHomography(source_points, destination, cv2.RANSAC, 5.0)

        warped_perspective = cv2.warpPerspective(image, homography_matrix, (target_width, target_height), cv2.INTER_CUBIC)

        final_image = cv2.cvtColor(src = warped_perspective, code = cv2.COLOR_BGR2RGB)
        return final_image

    def _unsharp_masking(self, image: np.ndarray) -> np.ndarray:
        gaussian = cv2.GaussianBlur(src = image, ksize = (0, 0), sigmaX = 2)
        return cv2.addWeighted(src1 = image, alpha = 1.5, src2 = gaussian, beta = -0.5, gamma = 0)

    def _bilateral_filter(self, image: np.ndarray) -> np.ndarray:
        return cv2.bilateralFilter(src = image, d = 9, sigmaColor = 75, sigmaSpace = 75)

    def _detail_enhance(self, image: np.ndarray) -> np.ndarray:
        return cv2.detailEnhance(src = image, sigma_s = 10, sigma_r = 0.15)

    def _noise_removal(self, image: np.ndarray) -> np.ndarray:
        return cv2.fastNlMeansDenoisingColored(src = image, h = 10, hColor = 10, templateWindowSize = 7, searchWindowSize = 21)