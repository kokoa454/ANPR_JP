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
        self.connectionStatus = False
    
    def run(self) -> None:
        while True:
            self.carDetected = self.deviceController.detectCar()

            if self.carDetected == False and self.detectionPaused == True:
                self.detectionPaused = False

            elif self.carDetected == True and self.detectionPaused == False:
                self.detectionPaused = True

                image = self.deviceController.captureNumberPlate()

                if image is not None:
                    numberPlateObject = self.recognizerController.recognizeNumberPlate(image = image)

                    if numberPlateObject is not None:
                        print(f"Recognized Number Plate: {numberPlateObject.getTypeOfVehicle()}\n{numberPlateObject.getRegionCode()}{numberPlateObject.getClassNum()} {numberPlateObject.getHiraganaCode()} {numberPlateObject.getRegistNum()}\n")
                        
                        day = self.utilities.getDay()
                        time = self.utilities.getTime()
                        regionCode = numberPlateObject.getRegionCode()
                        
                        self.connectionStatus = self.dataStoreController.checkDBConnection()
                        
                        if self.connectionStatus == True:
                            self.dataStoreController.insertOrUpdateVisitorsTable(day = day)
                            self.dataStoreController.insertIntoRegionCodeTable(day = day, time = time, regionCode = regionCode)
                        else:
                            pass # TODO: save to local database

                    else:
                        print("Number plate text not detected")

                else:
                    print("Number plate not detected")
                
            time.sleep(config.MAIN_LOOP_DELAY_SEC)  

if __name__ == "__main__":
    Main().run()
