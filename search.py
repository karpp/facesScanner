from facelist import Photo, Face, FaceList, find_similar
import os
from datetime import datetime

path = str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + '/'
os.makedirs(path + 'result')
os.makedirs(path + 'result_faces')

fl = FaceList('test', create=False)
fl.load()
my = Photo('input.jpg')
my.detect_faces()
myface = my.faces[0]
similars = find_similar(myface, fl)
print(similars)
for f in similars:
    fl.faces[f['persistedFaceId']].save(path)
print('Found {} faces.'.format(len(similars)))
