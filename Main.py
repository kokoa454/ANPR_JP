import DeviceController
import RecognizerController
import DataStoreController
import Utilities
import config
import time

class Main:
    def __init__(self) -> None:
        self.deviceController = DeviceController.DeviceController()
        self.recognizerController = RecognizerController.RecognizerController()
        self.dataStoreController = DataStoreController.DataStoreController()
        self.utilities = Utilities.Utilities()
        self.carDetected = False
        self.detectionPaused = False
    
    def run(self) -> None: # TODO: group each part of the loop into controllers and simplify this function
        while True:
            self.carDetected = self.deviceController.detectCar()

            if self.carDetected == False and self.detectionPaused == True:
                self.detectionPaused = False

            elif self.carDetected == True and self.detectionPaused == False:
                self.detectionPaused = True
                
                image = self.deviceController.captureNumberPlate()
                
                timeStamp = self.utilities.getTimeStamp()

                if image is not None:                 
                    numberPlateObject = self.recognizerController.recognizeNumberPlate(image = image)
                    
                    if numberPlateObject is not None:
                        print(f"Recognized Number Plate: {numberPlateObject.getTypeOfVehicle()}\n{numberPlateObject.getRegionCode()}{numberPlateObject.getClassNum()} {numberPlateObject.getHiraganaCode()} {numberPlateObject.getRegistNum()}\n")

                        if self.dataStoreController.checkBuffer() == True:
                            if self.dataStoreController.insertBufferDataToDB(timeStamp = timeStamp, numberPlateObject = numberPlateObject) == True:
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

                    else:
                        print("Number plate text not detected")

                else:
                    print("Number plate not detected")
                
            time.sleep(config.MAIN_LOOP_DELAY_SEC)

if __name__ == "__main__":
    Main().run()
