from controllers.device_controller import DeviceController
from controllers.datastore_controller import DatastoreController
from models.utilities import Utilities
import config.config as config
import time
import os

class Main:
    def __init__(self) -> None: 
        # Folder creation
        os.makedirs(config.OUTPUT_LOGS_DIR, exist_ok=True)
        os.makedirs(config.OUTPUT_BUFFER_DIR, exist_ok=True)

        # Controllers initialization
        self.device_controller = DeviceController.get_instance()
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

                    timestamp = Utilities.get_timestamp_for_db()

                    if self.datastore_controller.check_buffer() == True:
                        if self.datastore_controller.insert_buffer_data_to_db() == True:
                            print("退場データをバッファからDBに保存しました")
                        else:
                            print("退場データをバッファからDBに保存できませんでした")

                    if self.datastore_controller.insert_data_to_dB(timestamp = timestamp) == True:
                        print("退場データをDBに保存しました")
                    else:
                        print("退場データをDBに保存できませんでした")
                        
                        if self.datastore_controller.insert_data_to_buffer(timestamp = timestamp) == True:
                            print("退場データをバッファに保存しました")
                        else:
                            print("退場データをバッファに保存できませんでした")
                    
                time.sleep(config.MAIN_LOOP_DELAY_SEC)
                end_time = time.perf_counter()
                print(f"処理時間: {end_time - start_time} 秒")
        except KeyboardInterrupt:
            print("\nシステムをシャットダウンします")

if __name__ == "__main__":
    Main().run()
