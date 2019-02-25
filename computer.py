import base64
import cv2
import laneFinding
import numpy as np
import pathPlanning
import preprocessing
import time
import zmq

port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind("tcp://*:%s" % port)

src = np.float32([[20, 200], [350, 200],
                  [275, 120], [85, 120]])

img_size = [200, 360, 3]
dst = np.float32([[0, img_size[0]], [img_size[1], img_size[0]],
                  [img_size[1], 0], [0, 0]])

offset_angle = 0
while True:
    start_time = time.time()
    frame = socket.recv_pyobj()
    # frame = socket.recv_string()
    # img = base64.b64decode(frame)
    # npimg = np.fromstring(frame, dtype=np.uint8)
    source = cv2.imdecode(frame, 1)
    # source = cv2.resize(source, (1280, 720))

    # <editor-fold desc="Определение угла поворота">
    # Preprocessing
    combined_thresholded = preprocessing.colorthresh(source)
    warped_masked_img, M_warp, Minv = preprocessing.warp_image(combined_thresholded, src, dst, (img_size[1], img_size[0]))
    # lane finding
    ploty, lefty, righty, leftx, rightx, left_fitx, right_fitx, out_img = laneFinding.find_lane(warped_masked_img)
    # path planning
    center_fitx, center_offset = pathPlanning.calc_central_line(left_fitx, right_fitx, img_size, out_img, imshow=True)
    # center_fitx[-1] - last element in array, botton element of road centerangle = 1500
    vehicle_offset = pathPlanning.calculate_offset(img_size, center_fitx[-1])
    vehicle_offset_cm = pathPlanning.offset_in_centimeters(vehicle_offset, 20, left_fitx[-1], right_fitx[-1])
    # offset_angle = pathPlanning.calculate_offset_angle(vehicle_offset_cm, maximum_support_vehicle_offset=5, maximum_wheel_angle=15)

    # if offset_angle:
    #     angle = offset_angle
    # else:
    #     angle = 0
    socket.send_string(str(vehicle_offset_cm))
    # </editor-fold>

    # cv2.imshow("Stream", source)
    #
    if cv2.waitKey(1) == ord('q'):
        break
