from runner import Runner
from flask import Flask, render_template, send_file, Response
from pyngrok import ngrok
from time import sleep
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2
import io


app = Flask(__name__)
runner = Runner()
bufferFrames = []
liveStreamOn = False

@app.route("/")
def home():
    global liveStreamOn
    liveStreamOn = False
    return render_template("index.html")

@app.route("/files", defaults={"req_path":""})
@app.route("/files/<path:req_path>")
def dirListing(req_path):
    global liveStreamOn
    liveStreamOn = False

    BASE_DIR = os.path.abspath("output")

    absPath = os.path.join(BASE_DIR, req_path)

    # check if path does not exist
    if not os.path.exists(absPath):
        return "File not found"

    # check if phat is a file and serve
    if os.path.isfile(absPath):
        return send_file(absPath)

    # show directory contents
    files = os.listdir(absPath)

    prevFolder = "/".join(req_path.split("/")[:-1])
    prevFolder = "/files" + ("/" if prevFolder != "" else "") + prevFolder

    return render_template("files.html", files=files, prev=prevFolder)

@app.route("/live_stream")
def live():
    global liveStreamOn
    liveStreamOn = True
    if not runner.positionFixed:
        runner.getGPSData()

    return render_template("live_stream.html", coordinates=runner.convertToGPSDecimal())

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames(): 
    global liveStreamOn
    global bufferFrames
    
    for count,foo in enumerate(runner.camera.capture_continuous(runner.rawCapture , format="bgr", use_video_port=True)):
        
        if count % runner.cameraFrameRate == 0:
            bufferFrames.append(foo.array)

        ret, buffer = cv2.imencode('.jpg', foo.array)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

        # clear stream to get ready for next frame
        runner.rawCapture.seek(0)

        if not liveStreamOn:
            break

@app.route('/ndvi_feed')
def ndvi_feed():
    return Response(gen_ndvi_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_ndvi_frames():
    global liveStreamOn
    global bufferFrames
    
    fig, ax = plt.subplots(1,1)
    firstRun = True

    while liveStreamOn:
        if(len(bufferFrames) > 0):

            image = bufferFrames.pop(0)
            processedImage = runner.performNDVIOperation(image, format="BGR")

            im = ax.imshow(processedImage)

            if firstRun:
                firstRun = False
                fig.colorbar(im)

        
            ioBuff = io.BytesIO()
            fig.savefig(ioBuff, format='png')
            ioBuff.seek(0)

            yield (b'--frame\r\n'
                    b'Content-Type: image/png\r\n\r\n' + ioBuff.read() + b'\r\n')  # concat frame one by one and show result


if __name__ == "__main__":
    httpTunnel = ngrok.connect(addr=5000)
    print("==================== Server Connection information============================")
    print(f"Sever Link Details: {httpTunnel}")
    print("===================== Starting Connection ====================================")

    try:
        app.run()

    finally:
        runner.endConnection()
        runner.camera.close()
    
