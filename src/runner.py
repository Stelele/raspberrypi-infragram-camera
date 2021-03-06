from camera import Camera
from gps import GPS
from ndvi import NDVI
from exif import Image
import os


class Runner(Camera, GPS, NDVI):

    def __init__(self) -> None:
        Camera.__init__(self)
        GPS.__init__(self)
        NDVI.__init__(self)

    def tagNDVIImage(self, inputImage):
        print("getting GPS data")
        self.getGPSData()

        with open(inputImage, "rb") as img:
            fileImage = Image(img)

        fileImage.gps_latitude = (
            self.latitude["degrees"], self.latitude["minutes"], self.latitude["seconds"])
        fileImage.gps_latitude_ref = self.latitude["ref"]
        fileImage.gps_longitude = (
            self.longitude["degrees"], self.longitude["minutes"], self.longitude["seconds"])
        fileImage.gps_longitude_ref = self.longitude["ref"]

        with open(inputImage, "wb") as img:
            img.write(fileImage.get_file())


if __name__ == "__main__":
    jpgImageDirectory = "/".join(os.path.abspath(
        "output/images/jpg/_empty").split("/")[:-1])

    test = Runner()
    try:
        test.tagNDVIImage(f"{jpgImageDirectory}/rgbBluecalibration1_2.jpg")
    finally:
        test.endConnection()
