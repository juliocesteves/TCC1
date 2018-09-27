from face_detector import FaceDetector
from flask import Flask, render_template, Response

app = Flask(__name__)
imagefolder = "/Users/marceloaquino/Documents/Projetos/TCC/TCC1/tcc/test_recognition/Turmas/IARTIN1"
video_reference = 0
attendance_folder = "/Users/marceloaquino/Documents/Projetos/TCC/TCC1/tcc/test_recognition/Chamadas"
fd = FaceDetector(video_reference,imagefolder,attendance_folder)
fd.find_students_images()

@app.route('/')
def index():
    return render_template('index.html')

def gen():
    while True:
        frame = fd.process_web()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
