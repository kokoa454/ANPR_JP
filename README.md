# ANPR-JP

### This project is an Automatic Number Plate Recognizer for Raspberry Pi that possesses YOLO11n-based learning models for detecting and character recognition of Japanese vehicle identification plates (number plates).

![number-plate-pic-1](https://i.ibb.co/y7gkbT4/number-plate-pic1.jpg)

>Number of number plates and its information 
(普通_自家用　浜松 301　み ・778)

## JP Number Plate Format
### Markings

![number-plate-pic2](https://i.ibb.co/BHDTnG1r/number-plate-pic2.png)

| Position | Meaning |
| --- | --- |
| Top Left | Region Code |
| Top Right | Class Number |
| Bottom Left | Hiragana Code |
| Bottom Right | Registration Number |

### Color [^1]
| Number Plate Type | Engine Displacement | Background Color | Text Color |
| --- | --- | --- | --- | 
| 普通_自家用 | >= 660cc | White | Green |
| 普通_事業用 | >= 660cc | Green | White |
| 普通_自家用 | < 660cc | Yellow | Black |
| 普通_事業用 | < 660cc | Black | Yellow |


## Detection Approach
### ✨️yolo11n-seg-anpr-jp-detect
##### ① Input an image
##### ② Detect segments
##### ③ Find convex hulls
##### ④ Perform a projective transformation
##### ④ Hand a number plate image over to the OCR model

### ✨️yolo11n-anpr-jp-ocr
##### ① Receive a number plate image
##### ② Divide into two parts, top and bottom
##### ③ Detect characters
##### ④ Format texts
##### ⑤ Output formatted texts

## Usage of Machine Learning [^2]
### 1. Make Data Set For Detecting Number Plates [^3]
##### ① Set your API key On Roboflow
##### ② Set project key
##### ③ Download starts automatically

### 2. Start Machine Learning For Detecting Number Plates [^4]
##### ① Input an epochs number
##### ② Learning starts automatically with yolo11n-seg

### 3. Test Result for Detecting Number Plates [^5]
##### ① Put test images into ./generate_yolo_model/test_detect/
##### ② Set inference rate
##### ③ Test starts automatically

### 4. Make Data Set For OCR
##### ① Set a number of number plates, how many you want to generate
##### ② Generating starts automatically

### 5. Start Machine Learning For OCR [^6]
##### ① Input an epochs number
##### ② Learning starts automatically with yolo11n

### 6. Test Result for Detecting Number Plates [^7]
##### ① Put test images into ./generate_yolo_model/test_ocr/
##### ② Set inference rate
##### ③ Test starts automatically

## Usage of ANPR
### 1. Create .env file and make sure every params are filled in[^8]
```
# DETECTION SETTINGS
DETECTION_MODEL = yolo11n-seg-anpr-jp-detect.pt
DETECTION_IMG_SIZE = 640
DETECTION_CONFIDENCE = 0.5
DETECTION_IOU = 0.3
DETECTION_TARGET_WIDTH = 880
DETECTION_TARGET_HEIGHT = 440

# OCR SETTINGS
OCR_MODEL = yolo11n-anpr-jp-ocr.pt
OCR_IMG_SIZE = 640
OCR_CONFIDENCE = 0.5
OCR_IOU = 0.3
OCR_START_REGION_CODE_CLASS_ID = 4
UNDEFINED_TEXT = ???

# OUTPUT SETTINGS
OUTPUT_CAPTURE_DIR = ./outputs/capture
OUTPUT_DETECT_DIR = ./outputs/detect
OUTPUT_LOGS_DIR = ./logs

# RPICAM SETTINGS
CAMERA_ID = 0
RPICAM_METERING = spot
RPICAM_AUTOFOCUS_MODE = continuous
RPICAM_TIMEOUT = 2000

# TIME STAMP SETTINGS
TIME_STAMP_FORMAT = %Y%m%d_%H%M%S

```

[^1]: About Number Plate Color. In addition, there are special number plates in Japan, such as number plates with graphic backgrounds and diplomatic number plates, but the YOLO models included in this program cannot recognize number plates that are not listed in the table.

[^2]: About Usage Of Machine Learning. Users of this program can select menus by running ./generate_yolo_model/generate_yolo_model.py.

[^3]: About Data Set For Detecting Number Plates. The author used the project _"License Plate Computer Vision Model by Questions"_. Here is the [URL](https://universe.roboflow.com/questions/license-plate-1sowi).

[^4]: About Machine Learning For Detecting Number Plates. The author recommends users of this program to rename best.pt in ./generate_yolo_model/yolo_output_detect/number_plate_11n{n}_detect/weights into yolo11n-seg-anpr-jp-detect.pt.

[^5]: About Test Result for Detecting Number Plates. The test results will be put in ./generate_yolo_model/test_detect/results_images/.

[^6]: About Machine Learning For OCR. The author recommends users of this program to rename best.pt in ./generate_yolo_model/yolo_output_ocr/number_plate_11n{n}_ocr/weights into yolo11n-anpr-jp-ocr.pt.

[^7]: About Test Result for OCR. The test results will be put in ./generate_yolo_model/test_ocr/results_images/.

[^8]: About Params in .env. Boolean flags (`DETECTION_SAVE`, `OCR_SAVE`) are managed in `config.py` directly.
