import uuid

import numpy as np
import cv2
from flask import Flask, request, redirect

app = Flask(__name__)


def img_from_file_stream(f):
    return img_from_binary(f.read())


def img_from_binary(data):
    arr = np.fromstring(data, dtype='uint8')
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


@app.route('/api/search', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file_received = request.files['file']

        # img = img_from_file_stream(file_received)
        file_name = uuid.uuid4().hex
        with open(file_name, "wb") as fout:
            fout.write(file_received.read())
        # faces = face_processor.get_faces(img)

        return "file saved to {}".format(file_name)
    return '''Post image to this endpoint'''


@app.route('/')
def root():
    return "Hello, World!"
