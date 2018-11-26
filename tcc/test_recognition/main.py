from face_detector import FaceDetector
from flask import Flask, render_template, Response, jsonify, request
import json
import requests
import base64
from PIL import Image
import numpy as np
import io
import cv2

app = Flask(__name__)
imagefolder = "/Users/r3v0ltz/Desktop/TCC1/tcc/test_recognition/Turmas/IARTIN1"
image_folder_tecnofacens = "/Users/r3v0ltz/Desktop/TCC1/tcc/test_recognition/TF2018"
video_reference = 0
attendance_folder = "/Users/r3v0ltz/Desktop/TCC1/tcc/test_recognition/Chamadas"
fd = FaceDetector(video_reference,imagefolder,attendance_folder,image_folder_tecnofacens)
fd.find_students_images()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/proc_frame_view')
def proc_frame_view():
    return render_template('proc.html')


@app.route('/menu')
def menu():
    return render_template('menu.html')

# def gen():
#     i = 0
#     while True:
#         # if i == 20:
#         #     fd.find_new_students_images()
#         #     i = 0
#         # else:
#         #     i += 1
#         #frame = fd.process_web()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# @app.route('/video_feed')
# def video_feed():
#     return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

def relaxed_decode_base64(data):

    if '=' in data:
        data = data[:data.index('=')]

    missing_padding = len(data) % 4

    if missing_padding == 1:
        data += 'A=='

    elif missing_padding == 2:
        data += '=='
    elif missing_padding == 3:
        data += '='

    return base64.b64decode(data)


@app.route('/process_frame', methods=['POST'])
def process_frame():
    
    if request.method == "POST":
        if 'imageBase64' in request.form:
            image_b64 = request.form['imageBase64']
            decoded_img = relaxed_decode_base64(image_b64.split(',')[1])

            image = Image.open(io.BytesIO(decoded_img))
            image_converted = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
            data = fd.process_frame(image_converted)

    return data

@app.route('/get_reconhecidos', methods=['GET'])
def get_reconhecidos():
    return fd.get_reconhecidos()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)