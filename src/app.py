from runner import Runner
from flask import Flask, render_template, send_file
from pyngrok import ngrok
import os

app = Flask(__name__)
runner = Runner()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/files", defaults={"req_path":""})
@app.route("/files/<path:req_path>")
def dirListing(req_path):
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


if __name__ == "__main__":
    httpTunnel = ngrok.connect(addr=5000)
    print("==================== Server Connection information============================")
    print(f"Sever Link Details: {httpTunnel}")
    print("===================== Starting Connection ====================================")

    try:
        app.run()

    finally:
        runner.endConnection()
    
