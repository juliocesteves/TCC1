import os
import os.path
import cv2
import numpy as np
import face_recognition
from PIL import Image
from pprint import pprint
from os.path import basename
from datetime import datetime
from argparse import ArgumentParser

class FaceDetector(object):
    def __init__(self, video_reference, image_folder_path, attendance_folder_path):
        self.map_name_encode = {}
        self.list_images_faces = []
        self.folder_path = image_folder_path
        self.video_capture = cv2.VideoCapture(video_reference)
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.attendance_folder_path = attendance_folder_path
        # Initialize some variables
        self.face_locations = []
        self.face_encodings = []
        self.face_landmarks = []
        self.face_names = []
        self.process_this_frame = True

    def find_students_images(self):
        path = self.folder_path
        valid_images = [".jpg",".gif",".png"]
        for f in os.listdir(path):
            ext = os.path.splitext(f)[1]
            if ext.lower() not in valid_images:
                continue
            current_image = Image.open(os.path.join(path,f))
            if current_image:
                name = os.path.splitext(basename(os.path.join(path,f)))[0]

                current_image = current_image.convert('RGB')
                k_face = face_recognition.face_encodings(np.array(current_image))[0]
                if k_face.any():
                    self.map_name_encode[name] = k_face

    def process(self):
        while True:
            ret, frame = self.video_capture.read()

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            rgb_small_frame = small_frame[:, :, ::-1]

            if self.process_this_frame:
                self.face_locations = face_recognition.face_locations(rgb_small_frame)

                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

                self.face_landmarks = face_recognition.face_landmarks(rgb_small_frame, self.face_locations)

                self.face_names = []
                for face_encoding in self.face_encodings:
                    matches = face_recognition.compare_faces(list(self.map_name_encode.values()), face_encoding, tolerance=0.5)
                    name = "DESCONHECIDO"
                    
                    if True in matches:
                        first_match_index = matches.index(True)
                        name = list(self.map_name_encode.keys())[first_match_index]

                        self.save_attend(name)

                    self.face_names.append(name)

            self.process_this_frame = not self.process_this_frame


            for i in range(0,len(self.face_landmarks)):
                for j in range(1,68):
                    cv2.circle(frame, (self.face_landmarks[i][j][0]*4, self.face_landmarks[i][j][1]*4), 1, (255, 255, 255), thickness=-1)
            
            # Display the results
            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, bottom + 80), (right, bottom + 45), (0, 0, 0), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                red_value = 255
                green_value = 255
                blue_value = 255

                if name == "DESCONHECIDO":
                    green_value = 0
                    blue_value = 0

                cv2.putText(frame, name.upper(), (left + 10, bottom + 73 ), font, 1.0, (blue_value, green_value, red_value), 1)

            cv2.imshow('FaceDetector 1.0', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):          
                self.video_capture.release()
                cv2.destroyAllWindows()

    def save_attend(self, name):
        txt_log_name = str(self.folder_path).split("/")[-1] + "-" + str(self.current_date) + ".txt"
        full_path = self.attendance_folder_path + "/" + txt_log_name
        found = False
        try:
            with open(full_path) as file:
                current_data = file.read()
                if name in current_data:
                    found = True
        except Exception as identifier:
            pass
        
        with open(full_path,"a+") as file:
            if not found:
                file.write(name + "\n")

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-i", "--images", dest="imagefolder",default="/Users/marceloaquino/Documents/Projetos/Projs/test_recognition/Turmas/IARTIN1",
                        help="Folder with images", metavar="IMG")

    parser.add_argument("-o", "--output", dest="output",default="/Users/marceloaquino/Documents/Projetos/Projs/test_recognition/Chamadas",
                        help="Folder with output attendance text files", metavar="OUT")
    
    parser.add_argument("-v", "--video",dest="video", default=0,
                        help="Input value of the video reference")

    args = parser.parse_args()
    pprint(args)

    detector = FaceDetector(args.video, args.imagefolder, args.output)

    detector.find_students_images()
    detector.process()
