import RPi.GPIO as GPIO
import time
import serial


class GPS:

    def __init__(self) -> None:

        #set Pin 7 to Output Mode
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(7, GPIO.OUT)

        # variable to check if gps coordinates already obtained
        self.positionFixed = False 

        # store latitude information format {"degrees", "minutes", "seconds", "ref"}
        self.latitude = {} 

        # store latitude information format {"degrees", "minutes", "seconds", "ref"}
        self.longitude = {}

        #Turn on GPS Module
        while True:
            GPIO.output(7, GPIO.LOW)
            time.sleep(4)
            GPIO.output(7, GPIO.HIGH)
            break

        # setup UART connection
        self.ser = serial.Serial("/dev/serial0", 115200)

        # important AT commands for setting up GPS module
        W_buff = [b"AT+CGNSPWR=1\r\n", b"AT+CGNSSEQ=\"RMC\"\r\n",
                  b"AT+CGNSINF\r\n", b"AT+CGNSURC=2\r\n", b"AT+CGNSTST=1\r\n"]

        # Turn on GPS functionality on hardware module
        self.ser.write(W_buff[0])
        self.ser.flushInput()

        data = ""
        num = 1

        while True:
            
            # obtain output from serial interface
            while self.ser.inWaiting() > 0:
                data += self.ser.read(self.ser.inWaiting()).decode("utf-8")

            # write next AT command
            if data != "":
                time.sleep(0.5)

                if num < len(W_buff):
                    self.ser.write(W_buff[num])

                data = ""
                num += 1

                if num >= len(W_buff) + 5:
                    break

    def getGPSData(self):
        '''
            This function obtains the latitude and longitude coordinates from the GPS module
        '''

        data = ""

        while True:
            
            # obtain output from serial interface
            while self.ser.inWaiting() > 0:
                temp = self.ser.read(self.ser.inWaiting())
                data += temp.decode("utf-8")

            if data != "":
                #locate section of output with NMEA GNRMC format i.e. Time, date, position, course and speed 
                startLocation = data.find("GNRMC")

                if startLocation > -1:
                    endlocation = data.find("\n", startLocation+1) + 1

                    gpsData = data[startLocation:endlocation].split(",")

                    # check if successfully obtained latitude and longitude information
                    if(len(gpsData) > 3 and gpsData[2] == "A"):

                        self.positionFixed = True

                        # Store latitude information
                        lat = float(gpsData[3][:2]) + \
                            (float(gpsData[3][2:])/60)
                        self.latitude["degrees"] = float(int(lat))
                        latMinutes = (lat - self.latitude["degrees"]) * 60
                        self.latitude["minutes"] = float(int(latMinutes))
                        self.latitude["seconds"] = (
                            latMinutes - self.latitude["minutes"]) * 60
                        self.latitude["ref"] = gpsData[4]

                        # Store longitude information
                        long = float(gpsData[5][:3]) + \
                            (float(gpsData[5][3:])/60)
                        self.longitude["degrees"] = float(int(long))
                        longMinutes = (long - self.longitude["degrees"]) * 60
                        self.longitude["minutes"] = float(int(longMinutes))
                        self.longitude["seconds"] = (
                            longMinutes - self.longitude["minutes"]) * 60
                        self.longitude["ref"] = gpsData[6]

                        break

                    else:
                        self.positionFixed = False
                        print("Trying to fix data")

                time.sleep(0.5)
                data = ""

    def endConnection(self) -> None:
        '''
            This function properly stops and shutsdown the GPS module
        '''

        # Stop GPS Functionality
        time.sleep(0.5)
        self.ser.write(b"AT+CGNSPWR=0\r\n")
        self.ser.flushInput()
        time.sleep(1)

        # Turn off GPS module
        while True:
            GPIO.output(7, GPIO.LOW)
            time.sleep(4)
            GPIO.output(7, GPIO.HIGH)
            break

        # free GPIO pins
        GPIO.cleanup()

    def convertToGPSDecimal(self):
        '''
            Returns a list containing the latitude and longitude information using decimal format
        '''
        latNum = self.latitude["degrees"] + \
            (self.latitude["minutes"]/60) + \
            (self.latitude["seconds"]/3600)

        longNum = self.longitude["degrees"] + \
            (self.longitude["minutes"]/60) + \
            (self.longitude["seconds"]/3600)

        return [f"{latNum} {self.latitude['ref']}", f"{longNum} {self.longitude['ref']}"]


if __name__ == "__main__":

    # Show sample usage of GPS class and also time how long position fixing takes

    test = GPS()

    try:   

        for i in range(11):
            print(f"============Iteration {i}===============")
            start = time.time()
            test.getGPSData()
            end = time.time()
            print(f"Run Took: {end-start} seconds")
            print(test.convertToGPSDecimal())
            print("==========================================")

    finally:
        test.endConnection()
