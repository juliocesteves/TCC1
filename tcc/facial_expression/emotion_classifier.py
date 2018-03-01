import argparse
import dlib
import numpy as np
from .setup_facial import FACIALModel
# import tensorflow as tf
import sys
import cv2
import os
import time
import pandas as pd
import datetime
import operator
import traceback


def create_dirs(name = None):

    if name is None:
        name = str(datetime.datetime.now())

    return name


def save_csv(csv_data, name, video = False):

    col1 = 'frame' if video else 'image'

    columns = [col1, 'face', 'angry', 'disgust', 'fear', 'happy', 'sad', 'surprised', 'neutral', 'emotion']

    csv = pd.DataFrame(csv_data)

    path = os.getcwd()
    destiny = os.path.join(path, 'data')

    destiny = os.path.join(destiny, name)

    if not name.lower().endswith('.csv'):
        name += '.csv'

    file_name = os.path.join(destiny, name)

    csv = csv[columns]

    csv.to_csv(file_name, index=False)

    pass


def getAveragedEmotion(emotions, averages):

    aux = dict()

    for key, value in emotions.items():
        average = 0
        for v in averages[value.lower()]:
            average += v
        average /= len(averages[value.lower()])
        aux[value.lower()] = average

    return aux


def process_video(video_name, device, model, detector, predictor, emotions, name, num_average=1):

    csv_data = {'frame':[], 'face':[], 'angry':[], 'disgust':[], 'fear':[], 'happy':[], 'sad':[], 'surprised':[], 'neutral':[], 'emotion':[]}

    averages = dict()
    for k, v in emotions.items():
        averages[v.lower()] = []

    if video_name is None:
        cap = cv2.VideoCapture(device)
    else:
        cap = cv2.VideoCapture(video_name)

    if not cap.isOpened():
        print("Falha ao ler arquivo!")

    train_data = []

    frame_count = 0
    ret = True
    while ret:
        ret, frame = cap.read()

        if ret:

            try:

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame_count += 1
                for k, v in csv_data.items():
                    csv_data[k].append(0)
                csv_data['frame'][-1] = frame_count

                detections = detector(gray, 0)

                for k, d in enumerate(detections):
                    csv_data['face'][-1] = k

                    sub_face = gray[max(0, d.top()):min(gray.shape[1], d.bottom()), max(0, d.left()):min(gray.shape[1], d.right())]
                    resized = cv2.resize(sub_face, (48, 48), interpolation=cv2.INTER_AREA)
                    data = np.expand_dims(resized, axis=2)
                    data = data/255 - 0.5
                    train_data.append(data)
                    start_time = time.time()
                    emotion_levels = model.model.predict(np.array(train_data))
                    print("Time for prediction: " + str(time.time() - start_time))
                    train_data = []

                    if len(averages["angry"]) < num_average:
                        for key, value in emotions.items():
                            averages[value.lower()].append(emotion_levels[0][key])
                    else:
                        for key, value in emotions.items():
                            del averages[value.lower()][0]
                            averages[value.lower()].append(emotion_levels[0][key])

                    averaged_levels = getAveragedEmotion(emotions, averages)
                    emotion = max(averaged_levels.items(), key=operator.itemgetter(1))[0]

                    for key, value in emotions.items():
                        csv_data[value.lower()][-1] = np.float64(averaged_levels[value.lower()])
                    csv_data['emotion'][-1] = emotion

            except Exception as e:
                print(type(e))
                print(e.args)
                print(e)
                traceback.print_exception(e)
            # cv2.imshow("image", frame)

        # key = cv2.waitKey(1) & 0xFF
        #
        # if key == ord("l"):
        #     show_landmarks = not show_landmarks
        # elif key == ord("q"):
        #     break

    cap.release()
    cv2.destroyAllWindows()

    # save_csv(csv_data, name, video=True)

    return csv_data


def process_image_file(file_name, model, detector, predictor, emotions, name):

    csv_data = {'image':[], 'face':[], 'angry':[], 'disgust':[], 'fear':[], 'happy':[], 'sad':[], 'surprised':[], 'neutral':[], 'emotion':[]}

    # face_folder = os.path.join(os.getcwd(), 'client_site/facial_expression/data')
    # face_folder = os.path.join(face_folder, name)
    # face_folder = os.path.join(face_folder, 'faces')

    for k, v in csv_data.items():
        csv_data[k].append(0)

    csv_data['image'][-1] = file_name.split("/")[-1]

    train_data = []

    image = cv2.imread(file_name)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    detections = detector(gray, 1)

    for k, d in enumerate(detections):
        csv_data['face'][-1] = k
        sub_face = gray[d.top():d.bottom(), d.left():d.right()]
        # cv2.imwrite(os.path.join(face_folder, file_name.split("/")[-1].split('.')[0] + ".jpg"), sub_face)
        resized = cv2.resize(sub_face, (48, 48), interpolation=cv2.INTER_AREA)
        data = np.expand_dims(resized, axis=2)
        data = data/255 - 0.5
        train_data.append(data)
        try:
            emotion_levels = model.model.predict(np.array(train_data))
            train_data = []
            emotion = emotions[np.argmax(emotion_levels)]
            print(file_name + ": ")
            for key, value in emotions.items():
                csv_data[value.lower()][-1] = np.float64(emotion_levels[0][key])
                print(value + ": " + str(round(emotion_levels[0][key], 2)))
            csv_data['emotion'][-1] = emotion
            print("Predicted: " + emotion)
        except Exception as e:
            print(e)

    # save_csv(csv_data, name)

    return csv_data

def process_image_folder(folder_name, model, detector, predictor, emotions, name):

    csv_data = {'image':[], 'face':[], 'angry':[], 'disgust':[], 'fear':[], 'happy':[], 'sad':[], 'surprised':[], 'neutral':[], 'emotion':[]}

    for root, dirs, files in os.walk(folder_name, topdown=False):
        for file_name in files:

            file_name = os.path.join(root, file_name)

            face_folder = os.path.join(os.getcwd(), 'data')
            face_folder = os.path.join(face_folder, name)
            face_folder = os.path.join(face_folder, 'faces')

            for k, v in csv_data.items():
                csv_data[k].append(0)
            csv_data['image'][-1] = file_name.split("/")[-1].split('.')[0]

            train_data = []

            image = cv2.imread(file_name)

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            detections = detector(gray, 1)

            for k, d in enumerate(detections):
                csv_data['face'][-1] = k
                sub_face = gray[d.top():d.bottom(), d.left():d.right()]
                cv2.imwrite(os.path.join(face_folder, file_name.split("/")[-1].split('.')[0] + ".jpg"), sub_face)
                resized = cv2.resize(sub_face, (48, 48), interpolation = cv2.INTER_AREA)
                data = np.expand_dims(resized, axis=2)
                data = data/255 - 0.5
                train_data.append(data)
                try:
                    emotion_levels = model.model.predict(np.array(train_data))
                    train_data = []
                    emotion = emotions[np.argmax(emotion_levels)]
                    print(file_name + ": ")
                    for key, value in emotions.items():
                        csv_data[value.lower()][-1] = round(emotion_levels[0][key], 6)
                        print(value + ": "  + str(round(emotion_levels[0][key], 2)))
                    csv_data['emotion'][-1] = emotion
                    print("Predicted: " + emotion)
                except Exception as e:
                    print(e)

    save_csv(csv_data, name)

    pass

def initialize_parameters():

    model = FACIALModel(restore = os.path.join(os.getcwd(), "facial_expression/resnet50_imgsize48_weights.h5"))
    detector = dlib.get_frontal_face_detector()
    # detector = dlib.cnn_face_detection_model_v1("mmod_human_face_detector.dat")
    predictor = dlib.shape_predictor(os.path.join(os.getcwd(), "facial_expression/shape_predictor_68_face_landmarks.dat"))
    emotions = {0:"Angry", 1:"Disgust", 2:"Fear", 3:"Happy", 4:"Sad", 5:"Surprised", 6:"Neutral"}
    name = create_dirs()

    return model, detector, predictor, emotions, name

def main():

    model, detector, predictor, emotions, name = initialize_parameters()

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--video", help="Specify a video file.", type=str, default=None)
    group.add_argument("-i", "--image", help="Specify a image file.", type=str)
    group.add_argument("-if", "--image_folder", help="Specify a images folder.")
    group.add_argument("-d", "--device", help="Specify a device for video stream", type=int, default=None)
    parser.add_argument("-n", "--name", help="Specify a name for output files", type=str, default=None)

    args = parser.parse_args()

    if (not args.video is None or not args.device is None):
        process_video(args.video, args.device, model, detector, predictor, emotions, name)
    elif (args.image):
        process_image_file(args.image, model, detector, predictor, emotions, name)
    elif (args.image_folder):
        process_image_folder(args.image_folder, model, detector, predictor, emotions, name)

if __name__ == "__main__":
    main()
