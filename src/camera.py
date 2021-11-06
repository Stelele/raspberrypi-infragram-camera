from time import sleep
from picamera import PiCamera
from picamera.array import PiRGBArray
import os


class Camera:

    def __init__(self) -> None:
        self.camera = PiCamera()
        self.cameraResolution = (1024, 768)
        self.cameraFrameRate = 32
        self.camera.framerate = self.cameraFrameRate
        self.camera.resolution = self.cameraResolution
        self.rawCapture = PiRGBArray(self.camera)

        # allow camera to warmup
        sleep(0.1)

        self.videoRecordingStarted = False

    def captureRawImage(self, outputDirectory, outputFileName, exposure=1.5):
        '''
            Captures images and saves it in 24-bit RGB format
            Keyword arguments:
            -----------------
            outputDirectory: location of directory to save image
            outputFileName: name of output image 
            exposure: how long to pause before taking photo
        '''
        self.camera.resolution = self.cameraResolution
        self.camera.start_preview()
        sleep(exposure)
        self.camera.capture(f"{outputDirectory}/{outputFileName}.rgb", "rgb")

    def convertRawToJPG(self, inputFile, outputDirectory, outputFileName):
        '''
            Convert 24-bit RGB images to jpeg images
            Keyword arguments:
            -----------------
            inputFile: 24-bit RGB image to be converted
            outputDirectory: location of directory to save image
            outputFileName: name of output image 
        '''
        imageResolution = "x".join(map(str, self.cameraResolution))
        os.system(
            f"convert -size \"{imageResolution}\" -depth 8 -crop \"{imageResolution}\" {inputFile} {outputDirectory}/{outputFileName}.jpg")

    def recordVideoFor(self, outputDirectory, outputFileName, length=60, videoType='h264'):
        '''
            Record a video for a certain duration
            Keyword arguments:
            ------------------
            outputDirectory: location of directory to save image
            outputFileName: name of output image 
            length: duration of video recording
            videoType: format to save video file in
        '''
        self.camera.stop_preview()
        self.camera.resolution = self.cameraResolution
        self.videoRecordingStarted = True

        self.camera.start_recording(
            f"{outputDirectory}/{outputFileName}.{videoType}")
        self.camera.wait_recording(length)
        self.camera.stop_recording()

        self.videoRecordingStarted = False

    def recordVideo(self, outputDirectory, outputFileName, videoType="h264"):
        '''
            Record a video for an unknown duration
            Keyword arguments:
            ------------------
            outputDirectory: location of directory to save image
            outputFileName: name of output image 
            videoType: format to save video file in
        '''
        self.camera.stop_preview()
        self.camera.resolution = self.cameraResolution

        self.videoRecordingStarted = True

        self.camera.start_recording(
            f"{outputDirectory}/{outputFileName}.{videoType}")

    def stopVideoRording(self):
        '''
            Stop the recording started by recordVideo() function
        '''
        if self.videoRecordingStarted:
            self.camera.stop_recording()

    def convertVideoToMP4(self, inputVideo, outputDirectory, outputFileName):
        '''
            convert h264 videos to mp4
            Keyword arguments:
            -----------------
            inputVideo: video to be converted
            outputDirectory: location of directory to save image
            outputFileName: name of output image 
        '''
        os.system(f"ffmpeg -i '{inputVideo}' '{outputDirectory}/{outputFileName}.mp4'")


if __name__ == "__main__":
    test = Camera()

    rawImageDirectory = "/".join(os.path.abspath(
        "output/images/raw/_empty").split("/")[:-1])
    jpgImageDirectory = "/".join(os.path.abspath(
        "output/images/jpg/_empty").split("/")[:-1])
    rawVideoDirectory = "/".join(os.path.abspath(
        "output/videos/raw/_empty").split("/")[:-1])

    takePhoto = True

    if takePhoto:
        baseName = "rgbBluecalibration5"
        exposure = 2
        outputName = baseName + "_" + str(exposure).replace(".", "_")

        test.captureRawImage(rawImageDirectory, outputName, exposure)
        test.convertRawToJPG(
            f"{rawImageDirectory}/{outputName}.rgb", jpgImageDirectory, outputName)

    else:
        test.recordVideoFor(rawVideoDirectory, "IRcalibration")
        test.convertVideoToMP4(f"{rawVideoDirectory}/IRcalibration.h264", rawVideoDirectory, "test")
