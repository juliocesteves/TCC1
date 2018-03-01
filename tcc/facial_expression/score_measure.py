import os
import csv

file_list = ["angry.txt", "happy.txt", "disgust.txt", "neutral.txt", "surprise.txt", "sad.txt", "fear.txt"]
emotions = ["Angry", "Happy", "Disgust", "Neutral", "Surprise", "Sad", "Fear"]

for name in file_list:
    rows = 0
    true = 0
    with open(name) as f:
        reader = csv.reader(f)
        for row in reader:
            rows += 1
            for item in row:
                if item in emotions and name[:-4].capitalize() == item:
                    true += 1

    print(name[:-4].capitalize() + ":")
    print(true / rows)
