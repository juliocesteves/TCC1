from face_detector import FaceDetector
from flask import Flask, render_template, Response

app = Flask(__name__)
imagefolder = "C:/Users/Marcelo/Desktop/TCC1/tcc/test_recognition/Turmas/Todos"
image_folder_tecnofacens = "C:/Users/Marcelo/Desktop/TCC1/tcc/test_recognition/TF2018"
video_reference = 0
attendance_folder = "C:/Users/Marcelo/Desktop/TCC1/tcc/test_recognition/Chamadas"
fd = FaceDetector(video_reference,imagefolder,attendance_folder,image_folder_tecnofacens)
fd.find_students_images()

@app.route('/')
def index():
    return render_template('index.html')

def gen():
    i = 0
    while True:
        if i == 20:
            fd.find_new_students_images()
            i = 0
        else:
            i += 1
        frame = fd.process_web()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)