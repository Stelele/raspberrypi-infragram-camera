from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os

class NDVI:

    def __init__(self) -> None:
        self.imageWidth = 1024
        self.imageHeight = 768
        self.outputImageDirectory = "/".join(os.path.abspath("output/images/processed/_empty").split("/")[:-1])

    def analyzeImage(self, inputImage, outputFileName):
        imageFile = open(inputImage, "r+b")
        image = np.fromfile(imageFile, dtype=np.uint8).reshape((self.imageHeight, self.imageWidth, 3))

        redChannel = np.array(image[:, :, 0].tolist())
        blueChannel = np.array(image[:, :, 2].tolist())
        outputImage = (redChannel - blueChannel) / (redChannel + blueChannel)


        fig, ax = plt.subplots(1,1)
        im = ax.imshow(outputImage)
        fig.colorbar(im)
        plt.savefig(f"{self.outputImageDirectory}/{outputFileName}.jpg")

       


if __name__ == "__main__":
    test = NDVI()
    rawImageDirectory = "/".join(os.path.abspath("output/images/raw/_empty").split("/")[:-1])

    test.analyzeImage(f"{rawImageDirectory}/test.rgb", "testOutput")





