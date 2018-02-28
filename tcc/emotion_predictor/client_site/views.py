from django.shortcuts import render
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
import json
from django.core.files.storage import default_storage
from django.http import JsonResponse
import time
import requests
import os
import base64


def index(request):

    data = None
    if request.method == "POST":

        temp_file = request.FILES['file']

        if type(temp_file) is InMemoryUploadedFile:
            end = temp_file.name.split(".")[-1]
            path = default_storage.save('tmp/' + str(time.time()) + '.' + end, ContentFile(temp_file.read()))
            temp_file = path
        else:
            temp_file = request.FILES['file'].temporary_file_path()

        print("Iniciando processamento")

        full_path = os.path.join(os.getcwd(), temp_file)
        num_average = request.POST['num_frames']
        data = requests.post("http://127.0.0.1:5000/predict",
                             data=json.dumps({'file': full_path, 'num_average': num_average}),
                             headers={'content-type': 'application/json'},
                             ).content
        if type(data) is bytes:
            data = json.loads(data)

        print("Fim do processamento!")

    variables = {
        'data': data
    }

    return render(request, "index.html", variables)


def relaxed_decode_base64(data):

     # If there is already padding we strim it as we calculate padding ourselves.
    if '=' in data:
        data = data[:data.index('=')]

     # We need to add padding, how many bytes are missing.
    missing_padding = len(data) % 4

     # We would be mid-way through a byte.
    if missing_padding == 1:
        data += 'A=='
     # Jut add on the correct length of padding.
    elif missing_padding == 2:
        data += '=='
    elif missing_padding == 3:
     data += '='

     # Actually perform the Base64 decode.
    return base64.b64decode(data)


def index_json(request):
    if request.method == "POST":

        if 'imageBase64' in request.POST:
            image_b64 = request.POST['imageBase64']
            decoded_img = relaxed_decode_base64(image_b64.split(',')[1])
            path = default_storage.save('tmp/' + str(time.time()) + '.png', ContentFile(decoded_img))
            temp_file = path

        else:
            temp_file = request.FILES['file']

            if type(temp_file) is InMemoryUploadedFile:
                end = temp_file.name.split(".")[-1]
                path = default_storage.save('tmp/' + str(time.time()) + '.' + end, ContentFile(temp_file.read()))
                temp_file = path
            else:
                temp_file = request.FILES['file'].temporary_file_path()

        print("Iniciando processamento")

        full_path = os.path.join(os.getcwd(), temp_file)

        if 'num_frames' in request.POST:
            num_average = request.POST['num_frames']

        else:
            num_average = 1

        data = requests.post("http://127.0.0.1:5000/predict",
                             data=json.dumps({'file': full_path, 'num_average': num_average}),
                             headers={'content-type': 'application/json'},
                             ).content

        print("Fim do processamento!")

    return JsonResponse(json.loads(data))

