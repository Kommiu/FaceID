from imutils.video import VideoStream

from flask import Response
from flask import Flask
from flask import render_template

import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image, ImageDraw

import numpy as np
import threading
import argparse
import datetime
import imutils
import time
import cv2

outputFrame = None
lock = threading.Lock()

app = Flask(__name__)

vs = VideoStream(src=0).start()
device = torch.device('cpu')

mtcnn = MTCNN(
    image_size=160,
    margin=0,
    min_face_size=20,
    thresholds=[0.6, 0.7, 0.7],
    factor=0.709,
    post_process=True,
    device=device,
    keep_all=True,
)
# resnet = InceptionResnetV1(pretrained='cassia-webface').eval().to(device)


time.sleep(2.)

@app.route('/')
def index():
    return render_template('index.html')

def detect_face():
    global vs, outputFrame, lock, mtcnn

    while True:

        frame = vs.read()
        boxes, _ = mtcnn.detect(frame)
        if boxes is not None:
            for box in boxes:
                start = tuple(box[:2])
                end = tuple(box[2:])
                cv2.rectangle(frame, start, end, (0, 0, 255), 2)

        with lock:
            outputFrame = frame.copy() #np.array(im)


def generate():
    global outputFrame, lock

    while True:
        with lock:
            if outputFrame is None:
                continue
            (flag, encodedImage) = cv2.imencode('.jpg', outputFrame)
            if not flag:
                continue

        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
              bytearray(encodedImage) + b'\r\n')


@app.route('/video_feed')
def video_feed():

    return Response(
        generate(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
                    help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
                    help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
                    help="# of frames used to construct the background model")
    args = vars(ap.parse_args())

    t = threading.Thread(target=detect_face)
    t.daemon = True
    t.start()

    app.run(host=args['ip'], port=args['port'], debug=True, threaded=True, use_reloader=False)

vs.stop()
