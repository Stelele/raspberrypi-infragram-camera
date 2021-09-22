import RPi.GPIO as GPIO
import time
import serial

class GPS:

    def __init__(self) -> None:
        self.ser = serial.Serial("/dev/serial0", 115200)
        W_buff = [b"AT+CGNSPWR=1\r\n", b"AT+CGNSSEQ=\"RMC\"\r\n", b"AT+CGNSINF\r\n", b"AT+CGNSURC=2\r\n", b"AT+CGNSTST=1\r\n"]
        self.ser.write(W_buff[0])
        self.ser.flushInput()
        data = ""
        num = 1

        while True:
            while self.ser.inWaiting() > 0:
                data += self.ser.read(self.ser.inWaiting()).decode("utf-8")

            if data != "":
                print(data)
                time.sleep(0.5)

                if num < len(W_buff):
                    self.ser.write(W_buff[num])

                data = ""
                num += 1

                if num >= len(W_buff) + 5:
                    break

    def getData(self):

        data = ""

        while True:
            while self.ser.inWaiting() > 0:
                data += self.ser.read(self.ser.inWaiting()).decode("utf-8")

            if data != "":
                startLocation = data.find("GNRMC")
                
                if startLocation > -1:
                    endlocation = data.find("\n", startLocation+1) + 1
                    print(data[startLocation:endlocation])

                time.sleep(0.5)
                data = ""

    def endConnection(self) -> None:
        time.sleep(0.5)
        self.ser.write(b"AT+CGNSPWR=0\r\n")
        self.ser.flushInput()




if __name__ == "__main__":

    test = GPS()

    try:
        while True:
            test.getData()        

    except KeyboardInterrupt:
        test.endConnection()