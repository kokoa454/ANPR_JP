from Controllers.DeviceController import DeviceController
from Controllers.RecognizerController import RecognizerController
from Controllers.DatastoreController import DatastoreController
from Models.Utilities import Utilities
import config.config as config
from Models.NumberPlate import NumberPlate
import time
import os

class Main:
    def __init__(self) -> None: 
        # Folder creation
        os.makedirs(config.OUTPUT_DETECT_DIR, exist_ok=True)
        os.makedirs(config.OUTPUT_CAPTURE_DIR, exist_ok=True)
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
        while True:
            start_time = time.perf_counter()
            self.car_detected = self.device_controller.detect_car()

            if self.car_detected == False and self.detection_paused == True:
                self.detection_paused = False

            elif self.car_detected == True and self.detection_paused == False:
                self.detection_paused = True
                
                image = self.device_controller.capture_number_plate()
                
                number_plate_object = NumberPlate.NumberPlate()
                timestamp = Utilities.get_timestamp()

                if image is not None:
                    recognized_number_plate = self.recognizer_controller.recognize_number_plate(image = image, number_plate_object = number_plate_object)
                    
                    if recognized_number_plate is not None:
                        number_plate_object = recognized_number_plate
                        print(f"Recognized Number Plate: {number_plate_object.get_type_of_vehicle()}\n{number_plate_object.get_region_code()}{number_plate_object.get_class_num()} {number_plate_object.get_hiragana_code()} {number_plate_object.get_regist_num()}\n")

                    else:
                        print("Number plate text not detected")

                else:
                    print("Number plate not detected")

                if self.datastore_controller.check_buffer() == True:
                    if self.datastore_controller.insert_buffer_data_to_db() == True:
                        print("Buffer data inserted to DB successfully")
                    else:
                        print("Buffer data insertion to DB failed")

                if self.datastore_controller.insert_data_to_dB(timestamp = timestamp, number_plate_object = number_plate_object) == True:
                    print("Data inserted to DB successfully")
                else:
                    print("Data inserted to DB failed")
                    
                    if self.datastore_controller.insert_data_to_buffer(timestamp = timestamp, number_plate_object = number_plate_object) == True:
                        print("Data inserted to buffer successfully")
                    else:
                        print("Data inserted to buffer failed")

                del number_plate_object
                
            time.sleep(config.MAIN_LOOP_DELAY_SEC)
            end_time = time.perf_counter()
            print(f"Loop execution time: {end_time - start_time} seconds")

if __name__ == "__main__":
    Main().run()
