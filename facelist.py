import os
import requests
import json
from PIL import Image, ImageDraw
from io import BytesIO
from time import sleep
from datetime import datetime

subscription_key = '****'
base_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/'


def send_api_request(method, addr, headers=None, params=None, data=None):
    if method == 'get':
        response = requests.get(base_url + addr, headers=headers, params=params, data=data)
    if method == 'post':
        response = requests.post(base_url + addr, headers=headers, params=params, data=data)
    if method == 'put':
        response = requests.put(base_url + addr, headers=headers, data=data)
    if method == 'delete':
        response = requests.delete(base_url + addr, headers=headers)

    if response.status_code == 429:
        sleep(5)
        return send_api_request(method, addr, headers, params, data)
    return response


class Face:
    def __init__(self, faceId, imagePath, faceRectangle):
        self.faceId = faceId
        self.imagePath = imagePath
        self.data = open(imagePath, 'rb').read()
        self.faceRectangle = (faceRectangle['left'],
                              faceRectangle['top'],
                              faceRectangle['left'] + faceRectangle['width'],
                              faceRectangle['top'] + faceRectangle['height'])
        self.faceRectangleAzure = str(faceRectangle['left']) + ',' + str(faceRectangle['top']) + ',' + str(faceRectangle['width']) + ',' + str(faceRectangle['height'])

    def draw(self):
        image = Image.open(self.imagePath)
        draw = ImageDraw.Draw(image)
        draw.rectangle(self.faceRectangle, outline='green')
        del draw
        image.show()

    def save(self, prefix=''):
        image = Image.open(self.imagePath)
        image.save(prefix + 'result/{}.jpg'.format(self.faceId), 'JPEG')
        draw = ImageDraw.Draw(image)
        draw.rectangle(self.faceRectangle, outline='green')
        del draw
        image.save(prefix + 'result_faces/{}.jpg'.format(self.faceId), 'JPEG')


class Photo:
    def __init__(self, path):
        self.path = path
        self.data = open(path, 'rb').read()
        self.faces = []

    def detect_faces(self):
        headers = {'Ocp-Apim-Subscription-Key': subscription_key,
                   'Content-Type': 'application/octet-stream'}
        response = send_api_request('post', 'detect', headers=headers, data=self.data)
        print(response.content)
        response.raise_for_status()
        for face in response.json():
            self.faces.append(Face(face['faceId'], self.path, face['faceRectangle']))


class FaceList:
    def __init__(self, name, create=True):
        self.name = name
        self.faces = dict()
        self.url = 'facelists/{}'.format(self.name)
        if create:
            headers = {'Ocp-Apim-Subscription-Key': subscription_key,
                       'Content-Type': 'application/json'}
            # params = {'faceListId': name}
            data = {'name': name}
            response = send_api_request('put', self.url, headers=headers, data=json.dumps(data))
            print(response.content)
            response.raise_for_status()
            if response.status_code != 200:
                raise Exception(response.json())

    def load(self):
        headers = {'Ocp-Apim-Subscription-Key': subscription_key}
        response = send_api_request('get', 'facelists/{}'.format(self.name), headers=headers)
        print(response.content)
        response.raise_for_status()
        for fc in response.json()['persistedFaces']:
            faceid = fc['persistedFaceId']
            face_path = fc['userData'].split('@')[1]
            face_rect = list(map(int, fc['userData'].split('@')[0].split(',')))
            face_rectangle = {'left': face_rect[0], 'top': face_rect[1], 'width': face_rect[2], 'height': face_rect[3]}

            self.faces[fc['persistedFaceId']] = Face(faceid, face_path, face_rectangle)

    def add(self, face):
        # self.faces[face.faceId] = face
        headers = {'Ocp-Apim-Subscription-Key': subscription_key,
                   'Content-Type': 'application/octet-stream'}
        params = {'targetFace': face.faceRectangleAzure,
                  'userData': face.faceRectangleAzure + '@' + face.imagePath}
        data = face.data
        response = send_api_request('post', self.url + '/persistedFaces', headers=headers, params=params, data=data)
        # print(response.json())
        self.faces[response.json()['persistedFaceId']] = face
        return response.json()

    def delete(self):
        headers = {'Ocp-Apim-Subscription-Key': subscription_key}
        # params = {'faceListId': self.name}
        send_api_request('delete', self.url, headers=headers)


def find_similar(face, facelist):
    headers = {'Ocp-Apim-Subscription-Key': subscription_key,
               'Content-Type': 'application/json'}
    data = {'faceId': face.faceId,
            'faceListId': facelist.name,
            'maxNumOfCandidatesReturned': 1000}
    response = send_api_request('post', 'findsimilars', headers=headers, data=json.dumps(data))
    if response.status_code == 400:
        print(response.content)
    response.raise_for_status()
    return response.json()


def scan_dir(path):
    return os.listdir(path)