from flask import Flask, request, jsonify
from facial_expression import emotion_classifier
import tensorflow as tf


app = Flask(__name__)
model, detector, predictor, emotions, name = emotion_classifier.initialize_parameters()
graph = tf.get_default_graph()


@app.route("/predict", methods=['POST'])
def predict():

    if request.method == 'POST':
        try:
            data = request.get_json()
            temp_file = data['file']
            num_average = int(data['num_average'])

            with graph.as_default():
                if temp_file.lower().endswith(('.jpg', '.png', '.jpeg')):
                    result = emotion_classifier.process_image_file(temp_file, model, detector, predictor,
                                                                   emotions, name)
                else:
                    result = emotion_classifier.process_video(temp_file, None, model, detector, predictor, emotions,
                                                              name, num_average=num_average)
        except Exception as e:
            return jsonify(str(e))

        return jsonify(result)
    else:
        return jsonify('Only POST allowed')


if __name__ == '__main__':
    app.run(debug=True)
