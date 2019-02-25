import time
from threading import Thread
import cv2
import os
import zmq
import base64
import pigpio
import RPi.GPIO as GPIO
import numpy as np


from pid import Robot, run_PID_once

class Speed:
    def __init__(self):
        self.__speed = 0
        self.__count = 0

    def update_count(self):
        self.__count += 1

    def count_to_zero(self):
        self.__count = 0
        # self.speed = 1.78 / (self.current_time - self.last_time)

    def update_speed(self, count, delta_time):
        distance = float(count)/12.0 * 1.78
        self.__speed = distance/delta_time

    @property
    def get_speed(self):
        return self.__speed
    @property
    def get_count(self):
        return self.__count

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
# socket.bind("tcp://*:%s" % port)
socket.connect("tcp://192.168.31.172:%s" % port)


# Камера
path = "test_videos/"
file = "output1280.avi"
frameNumber = 0
img_size = [200, 360, 3]
cap = cv2.VideoCapture(path + file)

# GPIO
def change(channel):
    speed.update_count()

channel = 23
car_speed = 3  # cm per second
speed = Speed()

GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(channel, GPIO.BOTH, callback=change)

# PID
robot = Robot()
robot.set_noise(np.pi/48, 0)
robot.set_steering_drift(10.0/180 * np.pi)

robot_s = Robot()
robot_s.set_noise(0.5, 0)
robot_s.set_steering_drift(5)

# Управление мотором и рулем
os.system("sudo pigpiod")  # Launching GPIO library
time.sleep(1)  # As i said it is too impatient and so if this delay is removed you will get an error

ESC = 17
STEER = 18
pi = pigpio.pi()
pi.set_servo_pulsewidth(ESC, 0)
pi.set_servo_pulsewidth(STEER, 0)
time.sleep(1)
pi.set_servo_pulsewidth(ESC, 1500)
time.sleep(1)


if cap.isOpened() == False:
    print("Cannot open input video")
    exit()
# loop over some frames...this time using the threaded stream
while True:
    pi.set_servo_pulsewidth(ESC, 1550)
    # time.sleep(1)
    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 400 pixels
    start_time = time.time()
    frameNumber += 1
    ret, frame = cap.read()
    resized = cv2.resize(frame.copy(), (img_size[1], img_size[0]))
    cv2.imshow("frame", resized)
    # cv2.waitKey(0)

    # <editor-fold desc="тут должна быть отправка кадра на компьютер
    # и получение угла поворота в качестве ответа">


    # отправка кадра:
    encoded, buffer = cv2.imencode('.jpg', resized)
    # jpg_as_text = base64.b64encode(buffer)

    socket.send_pyobj(buffer)
    # socket.send(jpg_as_text)

    vehicle_offset_cm = float(socket.recv())

    # </editor-fold>


    # <editor-fold desc="вычисление необходимого ускорения">
    # ускорение от -50 до 50, среднее - 0,
    # скорость меняется от 1450 до 1350, среднее - 1400
    delta_time = time.time() - start_time
    speed.update_speed(speed.get_count, delta_time)
    current_speed = speed.get_speed
    speed.count_to_zero()

    # </editor-fold>

    # <editor-fold desc="Отправка сигналов машинке">
    # Вычисление PID
    # Для угла поворота:
    robot.set(0, vehicle_offset_cm, 0)
    # print(robot.y,robot.prew_y)
    x_t_PID, y_t_PID, steering = run_PID_once(robot, 2.5, 3.8, 0.5)
    # print("vehicle_offset_cm: {}, pid {}, steering: {} ".format(vehicle_offset_cm, y_t_PID, steering))

    # TODO возможно вычмсление не верное
    robot_s.set(0, car_speed - current_speed, 0)
    x_t_PID_speed, y_t_PID_speed, PID_speed = run_PID_once(robot_s, 0.5, 0.8, 0.1)
    print(current_speed)
    print("acc: {}, pid {}, speed: {} ".format(car_speed - current_speed, y_t_PID_speed, PID_speed))

    # </editor-fold>


    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break


# do a bit of cleanup
cv2.destroyAllWindows()
