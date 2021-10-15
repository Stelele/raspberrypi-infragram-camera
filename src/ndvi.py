from PIL import Image
from camera import Camera
from time import sleep
import numpy as np
import matplotlib.pyplot as plt
import os

class NDVI:

    def __init__(self) -> None:
        self.imageWidth = 1024
        self.imageHeight = 768
        self.outputImageDirectory = "/".join(os.path.abspath("output/images/processed/_empty").split("/")[:-1])
        self.rawImageDirectory = "/".join(os.path.abspath("output/images/raw/_empty").split("/")[:-1])

    def analyzeImage(self, inputImage, outputFileName, mode=0):

        if mode == 0:
            imageFile = open(inputImage, "r+b")
            image = np.fromfile(imageFile, dtype=np.uint8).reshape((self.imageHeight, self.imageWidth, 3))
        else:
            iImage = Image.open(inputImage)
            image = np.asarray(iImage)

        redChannel   = np.array(image[:, :, 0].tolist())
        greenChannel = np.array(image[:, :, 1].tolist())
        blueChannel  = np.array(image[:, :, 2].tolist())
        outputImage  = np.zeros((self.imageHeight, self.imageWidth))

        if mode == 0:
            redChannel  = 0.0299 * np.exp(0.0073  * (redChannel  + greenChannel))
            blueChannel = 0.019  * np.exp(0.0049  * (blueChannel + greenChannel))

            outputImage = (redChannel - blueChannel) / (redChannel + blueChannel)

        elif mode == 1:
            redChannel   = (redChannel - redChannel.min()) / (redChannel.max() - redChannel.min())
            greenChannel = (greenChannel - greenChannel.min()) / (greenChannel.max() - greenChannel.min())
            blueChannel  = (blueChannel - blueChannel.min()) / (blueChannel.max() - blueChannel.min())

            redChannel   = np.power((redChannel   + 0.055)/1.055,2.4)
            greenChannel = np.power((greenChannel + 0.055)/1.055,2.4)
            blueChannel  = np.power((blueChannel  + 0.055)/1.055, 2.4)

            transformation = np.array([[ -0.6168006001,  3.0321120793, -1.4276396748, 0.0494551008], \
                                        [-2.2981037998,  4.6453775652, -1.0628372695, 0.0485266687], \
                                        [-1.1373381041,  1.5107568513,  2.1166395585, 0.047374911], \
                                        [ 0.6987241741,  0.5488395299,  0.1258244845, 0.2757884897]])

            newImage = np.zeros((redChannel.shape[0], redChannel.shape[1], 4))

            for i in range(0,4,3):
                newImage[:,:,i] = transformation[i][0] * redChannel + transformation[i][1] * greenChannel + transformation[i][2] * blueChannel + transformation[i][3]

            outputImage = (newImage[:,:,0] - newImage[:,:,3])/(newImage[:,:,0] + newImage[:,:,3])
        
        elif mode == 2:
            outputImage = ((1.664 * blueChannel)/(0.953 * redChannel)) - 1

        else:
            outputImage = (redChannel - blueChannel) / (redChannel + blueChannel)

        #normalize data
        outputImage = (outputImage - outputImage.min()) / (outputImage.max() - outputImage.min())

        fig, ax = plt.subplots(1,1)
        #im = ax.imshow(outputImage, vmin=0,vmax=1, cmap="seismic")
        im = ax.imshow(outputImage)
        fig.colorbar(im)
        plt.savefig(f"{self.outputImageDirectory}/{outputFileName}.jpg")

       


if __name__ == "__main__":
    test = NDVI()
    rawImageDirectory = "/".join(os.path.abspath("output/images/raw/_empty").split("/")[:-1])
    jpgImageDirectory = "/".join(os.path.abspath("output/images/jpg/_empty").split("/")[:-1])
    NDVIMode = 0
    baseName = "rgbBluecalibration1"
    exposure = 2
    fileName = baseName + "_" + str(exposure).replace(".","_")
    #test.calibrate()

    if NDVIMode == 0:
        test.analyzeImage(f"{rawImageDirectory}/{fileName}.rgb", fileName + "_m"+str(NDVIMode))
    else:
        test.analyzeImage(f"{jpgImageDirectory}/{fileName}.jpg", fileName + "_m"+str(NDVIMode),NDVIMode)

    





