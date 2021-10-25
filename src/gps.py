import RPi.GPIO as GPIO
import time
import serial


class GPS:

    def __init__(self) -> None:

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(7, GPIO.OUT)

        self.positionFixed = False
        self.latitude = {}
        self.longitude = {}

        while True:
            GPIO.output(7, GPIO.LOW)
            time.sleep(4)
            GPIO.output(7, GPIO.HIGH)
            break

        self.ser = serial.Serial("/dev/serial0", 115200)
        W_buff = [b"AT+CGNSPWR=1\r\n", b"AT+CGNSSEQ=\"RMC\"\r\n",
                  b"AT+CGNSINF\r\n", b"AT+CGNSURC=2\r\n", b"AT+CGNSTST=1\r\n"]
        self.ser.write(W_buff[0])
        self.ser.flushInput()
        data = ""
        num = 1

        while True:
            while self.ser.inWaiting() > 0:
                data += self.ser.read(self.ser.inWaiting()).decode("utf-8")

            if data != "":
                # print(data)
                time.sleep(0.5)

                if num < len(W_buff):
                    self.ser.write(W_buff[num])

                data = ""
                num += 1

                if num >= len(W_buff) + 5:
                    break

    def getGPSData(self):

        data = ""
        self.runStart = True
        while True:
            while self.ser.inWaiting() > 0:
                data += self.ser.read(self.ser.inWaiting()).decode("utf-8")

            if data != "":
                startLocation = data.find("GNRMC")

                if startLocation > -1:
                    endlocation = data.find("\n", startLocation+1) + 1

                    gpsData = data[startLocation:endlocation].split(",")

                    if(len(gpsData) > 3 and gpsData[2] == "A"):
                        self.positionFixed = True

                        lat = float(gpsData[3][:2]) + \
                            (float(gpsData[3][2:])/60)
                        self.latitude["degrees"] = float(int(lat))
                        latMinutes = (lat - self.latitude["degrees"]) * 60
                        self.latitude["minutes"] = float(int(latMinutes))
                        self.latitude["seconds"] = (
                            latMinutes - self.latitude["minutes"]) * 60
                        self.latitude["ref"] = gpsData[4]

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
        time.sleep(0.5)
        self.ser.write(b"AT+CGNSPWR=0\r\n")
        self.ser.flushInput()
        time.sleep(1)

        while True:
            GPIO.output(7, GPIO.LOW)
            time.sleep(4)
            GPIO.output(7, GPIO.HIGH)
            break

        GPIO.cleanup()

    def convertToGPSDecimal(self):
        latNum = self.latitude["degrees"] + \
            (self.latitude["minutes"]/60) + \
            (self.latitude["seconds"]/3600)

        longNum = self.longitude["degrees"] + \
            (self.longitude["minutes"]/60) + \
            (self.longitude["seconds"]/3600)

        return [f"{latNum} {self.latitude['ref']}", f"{longNum} {self.longitude['ref']}"]


if __name__ == "__main__":

    test = GPS()

    for i in range(10):
        print(f"============Iteration {i}===============")
        test.getGPSData()
        print("==========================================")

    test.endConnection()
