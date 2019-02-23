import imutils
import time
from threading import Thread
import cv2
import os
import zmq
import base64

def acceleration_calc(speed):
    acc = speed
    return acc

class WebcamVideoStream:
    def __init__(self, src=0, name="WebcamVideoStream"):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        self.stream.set(3, 800)
        self.stream.set(4, 600)
        (self.grabbed, self.frame) = self.stream.read()

        # initialize the thread name
        self.name = name

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

# Сокет
port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind("tcp://*:%s" % port)

# Камера
src = 1
cam = '/dev/video%s' % src
os.system('v4l2-ctl -d %s -c exposure_auto=1' % cam)

vs = WebcamVideoStream(src=1).start()

# loop over some frames...this time using the threaded stream
while True:
    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 400 pixels
    start_time = time.time()
    frame = vs.read()
    # frame = imutils.resize(frame, width=640)

    # check to see if the frame should be displayed to our screen
    # encoded_image = cv2.imencode('.jpg', frame)

    cv2.imshow("Frame", frame)
    print(time.time() - start_time)

    # <editor-fold desc="тут должна быть отправка кадра на компьютер
    # и получение угла поворота в качестве ответа">

    # отправка кадра:
    encoded, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer)

    # socket.send_pyobj(buffer)
    socket.send(jpg_as_text)
    angle = socket.recv()
    print(int(angle))

    # </editor-fold>



    # <editor-fold desc="вычисление необходимого ускорения">
    speed = 1500

    # </editor-fold>

    # <editor-fold desc="Отправка сигналов машинке">

    # </editor-fold>

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

    # update the FPS counter

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
