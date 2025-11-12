__package__ = "NumberPlateRecognizer"

from PIL.Image import Image
from PIL import ImageDraw
import cv2
import numpy as np
from ultralytics import YOLO

class NumberPlateRecognizer:
    def __init__(self):
        self.model = YOLO("yolo11n-seg-anpr-jp-detect.pt")

    def detectNP(self, image: Image) -> Image | None:
        detectionResults = self.model(
            source = image,
            imgsz = 640,
            conf = 0.5,
            iou = 0.3,
            save = False
        )
        detections = detectionResults[0].boxes.xyxy
        masks = detectionResults[0].masks
        npNumber = len(detections)

        overlaidImage = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(overlaidImage)

        if masks is not None and npNumber > 0:
            segmentationMasks = masks.data.cpu().numpy()

            for i, mask in enumerate(segmentationMasks):
                boundingBox = detections[i]
                x1, y1, x2, y2 = map(int, boundingBox)
                resizedMask = self._createBinaryMask(mask, np.array(image))
                hull = self._detectConvexHull(resizedMask)
                if hull.size > 0:
                    mainHull = max(hull, key=cv2.contourArea)
                    rectangle = cv2.minAreaRect(mainHull)
                    boxPoints = cv2.boxPoints(rectangle)
                    sourcePoints = np.float32(boxPoints)
                    sortedPoints = self._sortSourcePoints(sourcePoints)

                if sourcePoints is not None:
                    npImage = self._transformPerspective(image, sortedPoints)
                else:
                    npImage = image[y1:y2, x1:x2]

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
        if contours:
            return cv2.convexHull(contours[0])
        return np.array([])
    
    def _sortSourcePoints(self, points: np.ndarray) -> np.ndarray:
        top = sorted(points[:2], key=lambda x: x[0])
        bottom = sorted(points[2:], key=lambda x: x[0], reverse=True)
        return np.array([top[0], top[1], bottom[0], bottom[1]], dtype="float32")
    
    def _transformPerspective(self, image: np.ndarray, sourcePoints: np.ndarray) -> Image:
        TARGET_WIDTH = 440 * 2
        TARGET_HEIGHT = 220 * 2

        destination = np.array([
            [0, 0], 
            [TARGET_WIDTH - 1, 0],
            [TARGET_WIDTH - 1, TARGET_HEIGHT - 1],
            [0, TARGET_HEIGHT - 1]
        ], dtype="float32")

        homographyMatrix, _ = cv2.findHomography(sourcePoints, destination, cv2.RANSAC, 5.0)
        
        warpedPerspective = cv2.warpPerspective(
            image, 
            homographyMatrix, 
            (TARGET_WIDTH, TARGET_HEIGHT),
            flags=cv2.INTER_CUBIC
        )
        
        finalImage = warpedPerspective
            
        return finalImage