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

    def analyzeImage(self, inputImage, outputFileName, mode=0):
        imageFile = open(inputImage, "r+b")
        image = np.fromfile(imageFile, dtype=np.uint8).reshape((self.imageHeight, self.imageWidth, 3))

        redChannel   = np.array(image[:, :, 0].tolist())
        greenChannel = np.array(image[:, :, 1].tolist())
        blueChannel  = np.array(image[:, :, 2].tolist())
        outputImage  = np.zeros((self.imageHeight, self.imageWidth))

        if mode == 0:
            redChannel  = (255 * redChannel   / self.imageWhiteBalanceValues["r"]).clip(0,255)
            blueChannel = (255 * blueChannel / self.imageWhiteBalanceValues["b"]).clip(0,255)
            outputImage = (redChannel - blueChannel) / (redChannel + blueChannel)

        elif mode == 1:
            redChannel   /= redChannel.max()
            greenChannel /= greenChannel.max()
            blueChannel  /= blueChannel.max()

            redChannel   = np.power((redChannel   + 0.055)/1.055,2.4)
            greenChannel = np.power((greenChannel + 0.055)/1.055,2.4)
            blueChannel  = np.power((blueChannel  + 0.055)/1.055, 2.4)

            transformation = np.array([[ -0.6168006001,  3.0321120793, -1.4276396748, 0.0494551008], \
                                        [-2.2981037998,  4.6453775652, -1.0628372695, 0.0485266687], \
                                        [-1.1373381041,  1.5107568513,  2.1166395585, 0.047374911], \
                                        [ 0.6987241741,  0.5488395299,  0.1258244845, 0.2757884897]])

            newImage = np.zeros((redChannel.shape[0], redChannel.shape[1], 4))

            for i in range(4):
                newImage[:,:,i] = transformation[i][0] * redChannel + transformation[i][1] * greenChannel + transformation[i][2] * blueChannel + transformation[i][3]

            outputImage = (newImage[:,:,0] - newImage[:,:,3])/(newImage[:,:,0] + newImage[:,:,3])
        
        else:
            outputImage = ((1.664 * blueChannel)/(0.953 * redChannel)) - 1

        fig, ax = plt.subplots(1,1)
        im = ax.imshow(outputImage)
        fig.colorbar(im)
        plt.savefig(f"{self.outputImageDirectory}/{outputFileName}.jpg")

       


if __name__ == "__main__":
    test = NDVI()
    rawImageDirectory = "/".join(os.path.abspath("output/images/raw/_empty").split("/")[:-1])

    test.calibrate()
    test.analyzeImage(f"{rawImageDirectory}/test1m3.rgb", "testOutput1m3",3)





