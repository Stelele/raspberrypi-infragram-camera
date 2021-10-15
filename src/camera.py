from time import sleep
from picamera import PiCamera
import os


class Camera:

    def __init__(self, mode=0) -> None:
        self.camera = PiCamera()
        self.cameraResolution = (1024, 768)

    def captureRawImage(self, outputDirectory, outputFileName, exposure=1.5):
        self.camera.resolution = self.cameraResolution
        self.camera.start_preview()
        sleep(exposure)
        self.camera.capture(f"{outputDirectory}/{outputFileName}.rgb","rgb")

    def convertRawToJPG(self, inputFile, outputDirectory, outputFileName):
        imageResolution = "x".join(map(str,self.cameraResolution))
        os.system(f"convert -size \"{imageResolution}\" -depth 8 -crop \"{imageResolution}\" {inputFile} {outputDirectory}/{outputFileName}.jpg")

if __name__ == "__main__":
    test = Camera()

    rawImageDirectory = "/".join(os.path.abspath("output/images/raw/_empty").split("/")[:-1])
    jpgImageDirectory = "/".join(os.path.abspath("output/images/jpg/_empty").split("/")[:-1])

    baseName = "rgbIRcalibration1"
    exposure=2
    outputName = baseName + "_" + str(exposure).replace(".","_")

    test.captureRawImage(rawImageDirectory, outputName,exposure)

    test.convertRawToJPG(f"{rawImageDirectory}/{outputName}.rgb", jpgImageDirectory, outputName)

