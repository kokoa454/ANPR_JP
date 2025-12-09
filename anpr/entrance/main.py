from controllers.device_controller import DeviceController
from controllers.recognizer_controller import RecognizerController
from controllers.datastore_controller import DatastoreController
from models.utilities import Utilities
import config.config as config
from models.number_plate import NumberPlate
import time
import os

class Main:
    def __init__(self) -> None: 
        # Folder creation
        os.makedirs(config.OUTPUT_DETECT_DIR, exist_ok=True)
        os.makedirs(config.OUTPUT_CAPTURE_DIR, exist_ok=True)
        os.makedirs(config.OUTPUT_OCR_DIR, exist_ok=True)
        os.makedirs(config.OUTPUT_LOGS_DIR, exist_ok=True)
        os.makedirs(config.OUTPUT_BUFFER_DIR, exist_ok=True)

        # Controllers initialization
        self.device_controller = DeviceController.get_instance()
        self.recognizer_controller = RecognizerController.get_instance()
        self.datastore_controller = DatastoreController.get_instance()
        
        # Variables
        self.car_detected = False
        self.detection_paused = False
    
    def run(self) -> None: # TODO: group each part of the loop into controllers and simplify this function
        try:
            print("システムをスタートアップします\n")
            while True:
                start_time = time.perf_counter()
                self.car_detected = self.device_controller.detect_car()

                if self.car_detected == False and self.detection_paused == True:
                    self.detection_paused = False

                elif self.car_detected == True and self.detection_paused == False:
                    self.detection_paused = True
                    print("車両を検出しました")

                    image = self.device_controller.capture_number_plate()
                    
                    number_plate_object = NumberPlate()
                    timestamp = Utilities.get_timestamp_for_db()

                    if image is not None:
                        recognized_number_plate = self.recognizer_controller.recognize_number_plate(image = image, number_plate_object = number_plate_object)
                        
                        if recognized_number_plate is not None:
                            number_plate_object = recognized_number_plate
                            print(f"ナンバープレートの文字認識結果: {number_plate_object.get_region_code()}{number_plate_object.get_class_num()} {number_plate_object.get_hiragana_code()} {number_plate_object.get_regist_num()}\n")

                        else:
                            print("ナンバープレート上の文字を認識できませんでした")

                    if self.datastore_controller.check_buffer() == True:
                        if self.datastore_controller.insert_buffer_data_to_db() == True:
                            print("ナンバープレートデータをバッファからDBに保存しました")
                        else:
                            print("ナンバープレートデータをバッファからDBに保存できませんでした")

                    if self.datastore_controller.insert_data_to_dB(timestamp = timestamp, number_plate_object = number_plate_object) == True:
                        print("ナンバープレートデータをDBに保存しました")
                    else:
                        print("ナンバープレートデータをDBに保存できませんでした")
                        
                        if self.datastore_controller.insert_data_to_buffer(timestamp = timestamp, number_plate_object = number_plate_object) == True:
                            print("ナンバープレートデータをバッファに保存しました")
                        else:
                            print("ナンバープレートデータをバッファに保存できませんでした")

                    del number_plate_object
                    
                time.sleep(config.MAIN_LOOP_DELAY_SEC)
                end_time = time.perf_counter()
                print(f"処理時間: {end_time - start_time} 秒")
        except KeyboardInterrupt:
            print("\nシステムをシャットダウンします")

if __name__ == "__main__":
    Main().run()
