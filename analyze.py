import os
from datetime import datetime
from facelist import Face, Photo, FaceList, scan_dir, find_similar


if __name__ == '__main__':

    BASEDIR = 'data'
    print(len(scan_dir(BASEDIR)), 'files')
    fl = FaceList('test')
    cnt = 0
    for p in scan_dir(BASEDIR):
        a = Photo(BASEDIR + '/' + p)
        a.detect_faces()
        for face in a.faces:
            fl.add(face)
            cnt += 1
            if cnt % 5 == 0:
                print('Added', cnt, 'faces')
            if cnt == 1000:
                break
        if cnt == 1000:
            break

    print("That's all.", cnt, 'faces totally.')

    path = str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + '/'
    os.makedirs(path + 'result')
    os.makedirs(path + 'result_faces')

    my = Photo('input.jpg')
    my.detect_faces()
    myface = my.faces[0]
    similars = find_similar(myface, fl)
    print(similars)
    for f in similars:
        fl.faces[f['persistedFaceId']].save(path)
    print('Found {} faces.'.format(len(similars)))
    # fl.delete()
