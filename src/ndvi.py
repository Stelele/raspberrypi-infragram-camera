from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os
import ffmpeg
import time


class NDVI:

    def __init__(self) -> None:
        # useful class information
        self.imageWidth = 1024
        self.imageHeight = 768
        self.outputImageDirectory = "/".join(os.path.abspath(
            "output/images/processed/_empty").split("/")[:-1])
        self.rawImageDirectory = "/".join(os.path.abspath(
            "output/images/raw/_empty").split("/")[:-1])
        self.rawVideoDirectory = "/".join(os.path.abspath(
            "output/videos/raw/_empty").split("/")[:-1])
        self.outputVideoDirectory = "/".join(os.path.abspath(
            "output/videos/processed/_empty").split("/")[:-1])

    def analyzeImage(self, inputImage, outputFileName, mode=0):
        '''
            Produces an NDVI image using one of 3 calibration techniques or direct NDVI implementation
            Keyword arguments:
            -----------------
            inputImage: Location of image to be processed
            outputFileName: Name  of output NDVI image
            mode: Determines which method to use to produce NDVI image
                    0: Use Calibration Targets Method
                    1: Use Linear Least Squares Technique
                    2: Use Relative Quantum Efficiency Technique
                    3: Use Unoptimized Direct NDVI implementation
                    4: Use Optimized Direct NDVI implementation
        '''

        # open images and load into numpy array
        if mode == 0:
            imageFile = open(inputImage, "r+b")
            image = np.fromfile(imageFile, dtype=np.uint8).reshape(
                (self.imageHeight, self.imageWidth, 3))
        
        else:
            iImage = Image.open(inputImage)
            image = np.asarray(iImage)

        # obtain NDVI image
        outputImage = self.performNDVIOperation(image, mode=mode, format="RGB")

        # Save processed image
        fig, ax = plt.subplots(1, 1)
        im = ax.imshow(outputImage)
        fig.colorbar(im)
        plt.savefig(f"{self.outputImageDirectory}/{outputFileName}.jpg")

    def analyzeVideo(self, inputVideo, outputFileName, mode=0):
        '''
            Produce an NDVI video and save to stated location
            Keyword arguments:
            -----------------
            inputVideo: Location of video to be processed
            outputFileName: Name  of output NDVI image
            mode: Determines which method to use to produce NDVI image
                    0: Use Calibration Targets Method
                    1: Use Linear Least Squares Technique
                    2: Use Relative Quantum Efficiency Technique
                    3: Use Unoptimized Direct NDVI implementation
                    4: Use Optimized Direct NDVI implementation
        '''
        
        # get video information
        probe = ffmpeg.probe(inputVideo)
        videoStream = next(
            (stream for stream in probe["streams"] if stream["codec_type"] == "video"), None)
        width = int(videoStream["width"])
        height = int(videoStream["height"])

        # load video frames into numpy array
        out, _ = (
            ffmpeg
            .input(inputVideo)
            .output("pipe:", format="rawvideo", pix_fmt="rgb24")
            .run(capture_stdout=True)
        )

        video = (
            np
            .frombuffer(out, np.uint8)
            .reshape((-1, height, width, 3))
        )

        # process video frames
        fig, ax = plt.subplots(1, 1)
        for i in range(video.shape[0]):
            outputImage = self.performNDVIOperation(video[i],mode=mode)

            im = ax.imshow(outputImage)

            if i == 0:
                fig.colorbar(im)

            plt.savefig(f"{self.outputVideoDirectory}/{i}.jpg")

        # recreate video from processed frames
        self.createVideo(outputFileName)

    def createVideo(self, outputName):
        '''
            Produce video from a collection of jpeg images
            Keyword arguments:
            -----------------
            outputName: Name of processed video
        '''
        (
            ffmpeg
            .input(f"{self.outputVideoDirectory}/*.jpg", pattern_type="glob", framerate=10)
            .output(f"{self.outputVideoDirectory}/{outputName}.mp4")
            .run()
        )

    def performNDVIOperation(self, inputArray, mode=0, format="RGB"):
        '''
            Carry out NDVI operations on numpy array which is either storing pixels as RGB or BGR
            Keyword arguments:
            -----------------
            inputArray: Array to be processed
            format: pixel array stored format ie RGB or BGR
            mode: Determines which method to use to produce NDVI image
                    0: Use Calibration Targets Method
                    1: Use Linear Least Squares Technique
                    2: Use Relative Quantum Efficiency Technique
                    3: Use Unoptimized Direct NDVI implementation
                    4: Use Optimized Direct NDVI implementation
            :param returns: processed numpy array
        '''

        # extract pixel channel frames
        redChannel = np.array(
            inputArray[:, :, 0 if format == "RGB" else 2].tolist())
        greenChannel = np.array(inputArray[:, :, 1].tolist())
        blueChannel = np.array(
            inputArray[:, :, 2 if format == "RGB" else 1].tolist())

        # array to store processed array
        outputImage = np.zeros((self.imageHeight, self.imageWidth))

        # process array using Calibration Targets Method
        if mode == 0:
            redChannel = 0.0299 * np.exp(0.0073 * (redChannel + greenChannel))
            blueChannel = 0.019 * np.exp(0.0049 * (blueChannel + greenChannel))

            outputImage = (redChannel - blueChannel) / \
                (redChannel + blueChannel)

        # process array using Linear Least Squares Technique
        elif mode == 1:
            redChannel = (redChannel - redChannel.min()) / \
                (redChannel.max() - redChannel.min())
            greenChannel = (greenChannel - greenChannel.min()) / \
                (greenChannel.max() - greenChannel.min())
            blueChannel = (blueChannel - blueChannel.min()) / \
                (blueChannel.max() - blueChannel.min())

            redChannel = np.power((redChannel + 0.055)/1.055, 2.4)
            greenChannel = np.power((greenChannel + 0.055)/1.055, 2.4)
            blueChannel = np.power((blueChannel + 0.055)/1.055, 2.4)

            transformation = np.array([[-0.6168006001,  3.0321120793, -1.4276396748, 0.0494551008],
                                       [-2.2981037998,  4.6453775652, -1.0628372695, 0.0485266687],
                                       [-1.1373381041,  1.5107568513,  2.1166395585, 0.047374911],
                                       [0.6987241741,  0.5488395299,  0.1258244845, 0.2757884897]])

            newImage = np.zeros((redChannel.shape[0], redChannel.shape[1], 4))

            for i in range(0, 4, 3):
                newImage[:, :, i] = transformation[i][0] * redChannel + transformation[i][1] * \
                    greenChannel + transformation[i][2] * \
                    blueChannel + transformation[i][3]

            outputImage = (newImage[:, :, 0] - newImage[:, :, 3]) / \
                (newImage[:, :, 0] + newImage[:, :, 3])

        # process array using Relative Quantum Efficiency Technique
        elif mode == 2:
            outputImage = ((1.664 * blueChannel)/(0.953 * redChannel)) - 1

        # process array using Unoptimized Direct NDVI implementation
        elif mode == 3:
            for row  in range(redChannel.shape[0]):
                for col in range(redChannel.shape[1]):
                    outputImage[row][col] = (redChannel[row][col] - blueChannel[row][col]) / (redChannel[row][col] + blueChannel[row][col])
        
        # process array using Optimized Direct NDVI implementation
        else:
            outputImage = (redChannel - blueChannel) / \
                (redChannel + blueChannel)

        # normalize data
        outputImage = (outputImage - outputImage.min()) / \
            (outputImage.max() - outputImage.min())

        return outputImage


if __name__ == "__main__":

    
    test = NDVI()
    rawImageDirectory = "/".join(os.path.abspath(
        "output/images/raw/_empty").split("/")[:-1])
    jpgImageDirectory = "/".join(os.path.abspath(
        "output/images/jpg/_empty").split("/")[:-1])
    rawVideoDirectory = "/".join(os.path.abspath(
        "output/videos/raw/_empty").split("/")[:-1])

    analyzeImage = True

    if analyzeImage:
        NDVIMode = 0
        baseName = "rgbBluecalibration2"
        exposure = 2
        fileName = baseName + "_" + str(exposure).replace(".", "_")

        for i in range(6):
            print(f"==================Iteration {i}====================")
            if NDVIMode == 0:
                start = time.time()
                test.analyzeImage(
                    f"{rawImageDirectory}/{fileName}.rgb", fileName + "_m"+str(NDVIMode), mode=NDVIMode)
                end = time.time()
            else:
                start = time.time()
                test.analyzeImage(f"{jpgImageDirectory}/{fileName}.jpg",
                                fileName + "_m"+str(NDVIMode), NDVIMode)
                end = time.time()

            print(f"Run took {end - start} seconds")
            print("======================================================")

    else:

        test.analyzeVideo(f"{rawVideoDirectory}/smallBluecalibration.mp4", "test")
        
