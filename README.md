# ANPR-JP

### This project is an Automatic Number Plate Recognizer for Raspberry Pi that possesses YOLO26m-based learning models for detecting and character recognition of Japanese vehicle identification plates (commonly known as ナンバープレート). Also this project owns api programs between Raspberry Pi and a server.

#### Folder Structure
##### YOLO Model Generator: `./yolo_model_generator`
##### ANPR on Raspberry Pi: `./anpr/entrance`
##### API Programs: `./anpr/server`

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
### ✨️yolo26m-seg-anpr-jp-detect
##### ① Input an image
##### ② Detect segments
##### ③ Find convex hulls
##### ④ Perform a perspective transformation
##### ⑤ Resize image
##### ⑥ Anti-sharp masking
##### ⑦ Bilateral filtering
##### ⑧ Detail enhancement
##### ⑨ Noise removal
##### ⑩ Hand a number plate image over to the OCR model

### ✨️yolo26m-anpr-jp-ocr
##### ① Receive a number plate image
##### ② Divide into two parts, top and bottom
##### ③ Detect characters
##### ④ Format texts
##### ⑤ Output formatted texts

## Installation
### 1. Make sure git and git lfs are installed
### 2. Run `git clone [the URL of this repository]` to clone this repository
### 3. Run `git lfs pull`, `git lfs fetch --all`, then `git lfs checkout` to get .pt files
### 4. Make sure Python 3.13.7 and pip are instaled
### 5. Run `pip install -r requirement.txt` in each folders 

## Usage of YOLO MODEL GENERATOR [^2]
### 1. Download fonts and put them into `./fonts/`
###### ・HiraginoMaruGothicProNW4.otf
###### ・TrmFontJB.ttf
###### ・FZcarnumberJA.otf

### 2. Make Data Set For Detecting Number Plates [^3]
##### ① Set your API key On Roboflow
##### ② Set project key
##### ③ Download starts automatically

### 3. Start Machine Learning For Detecting Number Plates [^4]
##### ① Input an epochs number
##### ② Learning starts automatically with yolo26m-seg

### 4. Test Result for Detecting Number Plates [^5]
##### ① Put test images into `./generate_yolo_model/test_detect/`
##### ② Set inference rate
##### ③ Test starts automatically

### 5. Make Data Set For OCR
##### ① Set a number of number plates, how many you want to generate
##### ② Generating starts automatically

### 6. Start Machine Learning For OCR [^6]
##### ① Input an epochs number
##### ② Learning starts automatically with yolo26m

### 7. Test Result for OCR [^7]
##### ① Put test images into `./generate_yolo_model/test_ocr/`
##### ② Set inference rate
##### ③ Test starts automatically

## Usage of ANPR on Raspberry Pi
### 1. Create `.env` files and make sure every params are filled in
```
# DETECTION SETTINGS
DETECTION_MODEL = ./yolo26m-seg-anpr-jp-detect.pt
DETECTION_IMG_SIZE = 1024
DETECTION_CONFIDENCE = 0.8
DETECTION_IOU = 0.3

# OCR SETTINGS
OCR_MODEL = ./yolo26m-anpr-jp-ocr.pt
OCR_IMG_SIZE = 1024
OCR_CONFIDENCE = 0.5
OCR_IOU = 0.3
OCR_START_REGION_CODE_CLASS_ID = 4
UNDEFINED_TEXT = UNDEFINED

# OUTPUT SETTINGS
OUTPUT_CAPTURE_DIR = ./outputs/capture
OUTPUT_DETECT_DIR = ./outputs/detect
OUTPUT_OCR_DIR = ./outputs/ocr
OUTPUT_LOGS_DIR = ./logs
OUTPUT_BUFFER_DIR = ./outputs/buffer
ERROR_LOG_FILE_NAME = error.log
BUFFER_JSON_FILE_NAME = buffer.json

# GMAIL SETTINGS
GMAIL_RECEIVER = YOUR_RECEIVER_EMAIL_ADDRESS
GMAIL_SENDER = YOUR_SENDER_EMAIL_ADDRESS
GMAIL_SCOPES = https://mail.google.com/
GMAIL_CREDENTIALS_FILE = ./credentials.json
GMAIL_TOKEN_FILE = ./token.json
GMAIL_DAILY_FIRST_SUBJECT = YOUR_DAILY_FIRST_SUBJECT
GMAIL_DAILY_FIRST_MESSAGE = YOUR_DAILY_FIRST_MESSAGE
GMAIL_ERROR_SUBJECT = YOUR_ERROR_SUBJECT
GMAIL_ERROR_MESSAGE = YOUR_ERROR_MESSAGE

# RPICAM SETTINGS
CAMERA_ID = 0
RPICAM_METERING = average
RPICAM_AUTOFOCUS_MODE = continuous
RPICAM_TIMEOUT = 500

# TIME STAMP SETTINGS
TIME_STAMP_FORMAT = %Y-%m-%d_%H:%M:%S
DATE_FORMAT = %Y-%m-%d

# PROXIMITY SENSOR SETTINGS
PROXIMITY_SENSOR_THRESHOLD_CM = 150.0
PROXIMITY_SENSOR_TRIGGER_PIN = 23
PROXIMITY_SENSOR_ECHO_PIN = 24
PROXIMITY_SENSOR_MAX_DISTANCE_METER = 4.5
PROXIMITY_SENSOR_OUT_OF_RANGE = OUT_OF_RANGE

# DB SETTINGS
API_NUMBER_PLATE_DATA_URL = YOUR_API_NUMBER_PLATE_DATA_URL
API_ERROR_DATA_URL = YOUR_API_ERROR_DATA_URL
API_KEY = YOUR_API_KEY
API_NAME = YOUR_API_NAME
DB_TIMEOUT_SEC = 1.0
RASPBERRY_PI_NUM = YOUR_RASPBERRY_PI_NUM

# MAIN SETTINGS
MAIN_LOOP_DELAY_SEC = 0.5
```

### 2. Run `python ./main.py`

## Usage of API Programs
### 1. Create `.env` files and make sure every params are filled in
```
# DB Settings
DATABASE_URL = YOUR_DATABASE_URL
API_KEY = YOUR_API_KEY
API_NAME = YOUR_API_NAME
```

### 2. Run `uvicorn main:app --host 0.0.0.0 --port 8000`


[^1]: About Number Plate Color. In addition, there are special number plates in Japan, such as number plates with graphic backgrounds and diplomatic number plates, but the YOLO models included in this program cannot recognize number plates that are not listed in the table.

[^2]: About Usage Of Machine Learning. Users of this program can select menus by running `./yolo_model_generator/yolo_model_generator.py`.

[^3]: About Data Set For Detecting Number Plates. The author used the project _"License plate final Computer Vision Model by demo"_. Here is the [URL](https://universe.roboflow.com/demo-z9q8y/license-plate-final-fgqza).

[^4]: About Machine Learning For Detecting Number Plates. The author recommends users of this program to rename best.pt in `./yolo_model_generator/yolo_output_detect/number_plate_26m{n}_detect/weights` into `yolo26m-seg-anpr-jp-detect.pt`.

[^5]: About Test Result for Detecting Number Plates. The test results will be put in `./yolo_model_generator/test_detect/results_images/`.

[^6]: About Machine Learning For OCR. The author recommends users of this program to rename best.pt in `./yolo_model_generator/yolo_output_ocr/number_plate_26m{n}_ocr/weights` into `yolo26m-anpr-jp-ocr.pt`.

[^7]: About Test Result for OCR. The test results will be put in `./yolo_model_generator/test_ocr/results_images/`.
