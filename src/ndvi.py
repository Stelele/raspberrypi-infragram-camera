from PIL import Image
from camera import Camera
import numpy as np
import matplotlib.pyplot as plt
import os

class NDVI:

    def __init__(self) -> None:
        self.imageWidth = 1024
        self.imageHeight = 768
        self.outputImageDirectory = "/".join(os.path.abspath("output/images/processed/_empty").split("/")[:-1])
        self.rawImageDirectory = "/".join(os.path.abspath("output/images/raw/_empty").split("/")[:-1])
        self.imageWhiteBalanceValues = {"r":255, "g":255, "b":255}

    def calibrate(self):
        print("Getting White Balance Parameters")
        cam = Camera()
        cam.captureRawImage(self.rawImageDirectory,"white")

        whiteImage = np.fromfile(f"{self.rawImageDirectory}/white.rgb", dtype=np.uint8).reshape((self.imageHeight, self.imageWidth, 3))
        self.imageWhiteBalanceValues["r"] = int(whiteImage[:,:,0].max())
        self.imageWhiteBalanceValues["g"] = int(whiteImage[:,:,1].max())
        self.imageWhiteBalanceValues["b"] = int(whiteImage[:,:,2].max())

    def analyzeImage(self, inputImage, outputFileName):
        imageFile = open(inputImage, "r+b")
        image = np.fromfile(imageFile, dtype=np.uint8).reshape((self.imageHeight, self.imageWidth, 3))

        redChannel = (255 * np.array(image[:, :, 0].tolist()) / self.imageWhiteBalanceValues["r"]).clip(0,255)
        blueChannel = (255 * np.array(image[:, :, 2].tolist())/ self.imageWhiteBalanceValues["b"]).clip(0,255)
        
        outputImage = (redChannel - blueChannel) / (redChannel + blueChannel)


        fig, ax = plt.subplots(1,1)
        im = ax.imshow(outputImage)
        fig.colorbar(im)
        plt.savefig(f"{self.outputImageDirectory}/{outputFileName}.jpg")

       


if __name__ == "__main__":
    test = NDVI()
    rawImageDirectory = "/".join(os.path.abspath("output/images/raw/_empty").split("/")[:-1])

    test.calibrate()
    test.analyzeImage(f"{rawImageDirectory}/test4.rgb", "testOutput4")





