import cv2
import numpy as np


def calc_central_line(left_fitx, right_fitx, img_size, central_line_img, imshow=False):
    '''
    1. Вычисление центральной линии по точкам левой и правой линии
    2. Определение смещения от центра в каждой точке центральной линии

    '''
    # центральная линия
    centr_fitx = ((right_fitx - left_fitx) / 2) + left_fitx
    # Смещение центральной линии по точкам
    centr_offset = centr_fitx - (img_size[1] / 2)

    if imshow == True:
        # Отрисовка центральной линии на изображении
        for i in range(len(centr_fitx)):
            cv2.circle(central_line_img, (int(centr_fitx[i]), i), 1, (255, 50, 255))
        cv2.imshow("central_line_img", central_line_img)

    # evklid_distance = np.linalg.norm(centr_fitx - prew_center_fitx)
    # print(evklid_distance)
    # cv2.waitKey(0)
    # prew_center_fitx = centr_fitx

    return centr_fitx, centr_offset


def calculate_offset(img_size, bottom_centr_fitx):
    """Вычисляем смещение шасси от центральной линии на изображении
    Смещение в пикселях
    """
    img_center = img_size[1] / 2
    # print(img_center, bottom_centr_fitx)

    vehicle_offset = (img_center - bottom_centr_fitx)

    # print(vehicle_offset)
    return vehicle_offset


def offset_in_centimeters(vehicle_offset, road_width_cm, bottom_left_fitx, bottom_right_fitx):
    if bottom_right_fitx != bottom_left_fitx:
        return vehicle_offset / ((bottom_right_fitx - bottom_left_fitx) / road_width_cm)
    else:
        return vehicle_offset / ((bottom_left_fitx) / road_width_cm)

    ## TODO есть деление на ноль при исчезновении одной из линий поля разметки
    # TODO Надо переписать, если линии совпадают, то центр такой же, как и линии
    # TODO с пометкой с какой стороны он был в последний раз (чтобы отслеживать где появится линия

# def centimeters_per_pixel(pixels):
#
#
#     return centimeters

def calculate_offset_angle(vehicle_offset_centimeters, maximum_support_vehicle_offset=5, maximum_wheel_angle=30):
    """ Вычисление угла поворота колес исходя из текущего
    положения автомобиля (offset in centimeters)  - смещения по горизонтали от центра.
    """
    offset_angle = 0

    # смещение влево
    if vehicle_offset_centimeters >= maximum_support_vehicle_offset:
        offset_angle = maximum_wheel_angle
    # смещение вправо
    elif vehicle_offset_centimeters <= -maximum_support_vehicle_offset:
        offset_angle = -maximum_wheel_angle
    else:
        offset_angle = (maximum_wheel_angle / maximum_support_vehicle_offset) * vehicle_offset_centimeters

    return offset_angle
