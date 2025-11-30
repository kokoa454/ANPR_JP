from Controllers.DeviceController import DeviceController
from Controllers.RecognizerController import RecognizerController
from Controllers.DataStoreController import DataStoreController
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
        self.deviceController = DeviceController.getInstance()
        self.recognizerController = RecognizerController.getInstance()
        self.dataStoreController = DataStoreController.getInstance()
        
        # Variables
        self.carDetected = False
        self.detectionPaused = False
    
    def run(self) -> None: # TODO: group each part of the loop into controllers and simplify this function
        while True:
            startTime = time.perf_counter()
            self.carDetected = self.deviceController.detectCar()

            if self.carDetected == False and self.detectionPaused == True:
                self.detectionPaused = False

            elif self.carDetected == True and self.detectionPaused == False:
                self.detectionPaused = True
                
                image = self.deviceController.captureNumberPlate()
                
                numberPlateObject = NumberPlate.NumberPlate()
                timeStamp = Utilities.getTimeStamp()

                if image is not None:
                    recognizedNumberPlate = self.recognizerController.recognizeNumberPlate(image = image, numberPlateObject = numberPlateObject)
                    
                    if recognizedNumberPlate is not None:
                        numberPlateObject = recognizedNumberPlate
                        print(f"Recognized Number Plate: {numberPlateObject.getTypeOfVehicle()}\n{numberPlateObject.getRegionCode()}{numberPlateObject.getClassNum()} {numberPlateObject.getHiraganaCode()} {numberPlateObject.getRegistNum()}\n")

                    else:
                        print("Number plate text not detected")

                else:
                    print("Number plate not detected")

                if self.dataStoreController.checkBuffer() == True:
                    if self.dataStoreController.insertBufferDataToDB() == True:
                        print("Buffer data inserted to DB successfully")
                    else:
                        print("Buffer data insertion to DB failed")

                if self.dataStoreController.insertDataToDB(timeStamp = timeStamp, numberPlateObject = numberPlateObject) == True:
                    print("Data inserted to DB successfully")
                else:
                    print("Data inserted to DB failed")
                    
                    if self.dataStoreController.insertDataToBuffer(timeStamp = timeStamp, numberPlateObject = numberPlateObject) == True:
                        print("Data inserted to buffer successfully")
                    else:
                        print("Data inserted to buffer failed")
                
            time.sleep(config.MAIN_LOOP_DELAY_SEC)
            endTime = time.perf_counter()
            print(f"Loop execution time: {endTime - startTime} seconds")

if __name__ == "__main__":
    Main().run()
