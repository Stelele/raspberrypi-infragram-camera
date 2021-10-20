from camera import Camera
from gps import GPS
from ndvi import NDVI


class Runner(Camera, GPS, NDVI):

    def __init__(self) -> None:
        Camera.__init__(self)
        GPS.__init__(self)
        NDVI.__init__(self)

    def tagNDVIImage(self, inputImage):
        print("getting GPS data")
        self.getData()



if __name__ == "__main__":
    test = Runner()
    test.tagNDVIImage("test")
    test.endConnection()