import zmq
import random
import sys
import time
import cv2
import base64
import numpy as np

port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://localhost:%s" % port)

while True:

    # frame = socket.recv_pyobj()
    frame = socket.recv_string()
    img = base64.b64decode(frame)
    npimg = np.fromstring(img, dtype=np.uint8)

    source = cv2.imdecode(npimg, 1)
    # source = cv2.resize(source, (1280, 720))

    # <editor-fold desc="Тут должны быть некоторые операции по
    # определению угла поворота">
    angle = 1500
    # Отправка угла поворота
    socket.send_string(str(angle))
    # </editor-fold>

    cv2.imshow("Stream", source)
    # print(source)
    if cv2.waitKey(1) == ord('q'):
        break
