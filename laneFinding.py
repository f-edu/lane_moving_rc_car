# ## Finding the Lane Line ##
# In[2]:
import numpy as np
import collections
import cv2

class Line():
    def __init__(self):
        # Was the line detected in the last iteration?
        self.detected = False
        # x values of the last n fits of the line
        self.recent_xfitted = collections.deque(12 * [0.0, 0.0, 0.0], 12)
        # Average x values of the fitted line over the last n iterations
        self.bestx = None
        # Polynomial coefficients averaged over the last n iterations
        self.best_fit = None
        # Polynomial coefficients for the most recent fit
        self.current_fit = [np.array([False])]
        # Radius of curvature of the line in some units (meters)
        self.radius_of_curvature = None
        # Distance in meters of vehicle center from the line
        self.line_base_pos = None
        # difference in fit coefficients between last and new fits
        self.diffs = np.array([0, 0, 0], dtype='float')
        # x values for detected line pixels
        self.allx = None
        # y values for detected line pixels
        self.ally = None




left_lane = Line()
right_lane = Line()



def find_base(binary_warped):
    histogram = np.sum(binary_warped[binary_warped.shape[0] // 2:, :], axis=0)
    midpoint = np.int(histogram.shape[0] / 2)
    leftx_base = np.argmax(histogram[:midpoint])
    rightx_base = np.argmax(histogram[midpoint:]) + midpoint

    return leftx_base, midpoint, rightx_base

# left_lane = Line()
# right_lane = Line()

def find_lane(binary_warped):
    flag_same_lines = False

    leftx_base, midpoint, rightx_base = find_base(binary_warped)
    # print(leftx_base, midpoint, rightx_base)
    # при 0 значении left base
    out_img = np.dstack((binary_warped, binary_warped, binary_warped)) * 255

    # cv2.imshow("out_img",out_img)
    nwindows = 9
    window_height = np.int(binary_warped.shape[0] / nwindows)
    # 10 частей по 20 px. высота окна = 20
    # print(window_height)

    nonzero = binary_warped.nonzero()
    # Индексы не нулевых элементов python
    # print(nonzero)

    # cv2.waitKey(0)
    nonzeroy = np.array(nonzero[0])
    # индексы по x

    nonzerox = np.array(nonzero[1])
    # индексы по y

    leftx_current = leftx_base
    rightx_current = rightx_base

    # margin = 100
    # minpix = 50
    margin = 100
    minpix = 50

    left_lane_inds = []
    right_lane_inds = []

    # Will start the search from scratch for first frame and then will use margin window
    # If the sanity fails then will search from scratch
    if (left_lane.detected == False) or (right_lane.detected == False):
        # Если левой или правой линии не найдено то:

        for window in range(nwindows):
            # Identify window boundaries in x and y (and right and left)
            win_y_low = binary_warped.shape[0] - (window + 1) * window_height
            win_y_high = binary_warped.shape[0] - window * window_height
            # print(win_y_low,win_y_high)

            win_xleft_low = leftx_current - margin
            win_xleft_high = leftx_current + margin
            win_xright_low = rightx_current - margin
            win_xright_high = rightx_current + margin
            # print(win_xleft_low)

            # Identify the nonzero pixels in x and y within the window
            good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xleft_low) & (
                        nonzerox < win_xleft_high)).nonzero()[0]
            good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xright_low) & (
                        nonzerox < win_xright_high)).nonzero()[0]

            # Append these indices to the lists
            left_lane_inds.append(good_left_inds)
            # print("__________________")
            # print(left_lane_inds)
            # print("__________________")
            right_lane_inds.append(good_right_inds)

            if len(good_left_inds) > minpix:
                leftx_current = np.int(np.mean(nonzerox[good_left_inds]))
                # print(leftx_current)
            if len(good_right_inds) > minpix:
                rightx_current = np.int(np.mean(nonzerox[good_right_inds]))

        # Concatenate the arrays of indices
        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)
        left_lane.detected = True
        right_lane.detected = True

    else:
        left_lane_inds = ((nonzerox > (left_lane.current_fit[0] * (nonzeroy ** 2) +
                                       left_lane.current_fit[1] * nonzeroy +
                                       left_lane.current_fit[2] - margin)) &
                          (nonzerox < (left_lane.current_fit[0] * (nonzeroy ** 2) +
                                       left_lane.current_fit[1] * nonzeroy +
                                       left_lane.current_fit[2] + margin)))
        right_lane_inds = ((nonzerox > (right_lane.current_fit[0] * (nonzeroy ** 2) +
                                        right_lane.current_fit[1] * nonzeroy +
                                        right_lane.current_fit[2] - margin)) &
                           (nonzerox < (right_lane.current_fit[0] * (nonzeroy ** 2) +
                                        right_lane.current_fit[1] * nonzeroy +
                                        right_lane.current_fit[2] + margin)))

    # Extract left and right line pixel positions
    leftx = nonzerox[left_lane_inds]
    lefty = nonzeroy[left_lane_inds]


    rightx = nonzerox[right_lane_inds]
    righty = nonzeroy[right_lane_inds]
    # print(len(leftx))
    # print(len(rightx))
    # cv2.waitKey(0)
    # Saving successful pixel position values to the respective Line objects
    # количество пикселей в распознанной разметке.
    if (len(leftx) < 800):
    # if (len(leftx) < 1500):
        leftx = left_lane.allx
        lefty = left_lane.ally
        left_lane.detected = False
    else:
        left_lane.allx = leftx
        left_lane.ally = lefty
    if (len(rightx) < 800):
    # if (len(rightx) < 1500):
        rightx = right_lane.allx
        righty = right_lane.ally
        right_lane.detected = False
    else:
        right_lane.allx = rightx
        right_lane.ally = righty
    # # Возвращение на дорогу с линии. Когда длины массивов равны, принимает обе линии за одну, расположение левой и правой линии становится одинаковым
    #
    if (len(leftx)==len(rightx)):
        leftx = left_lane.allx
        lefty = left_lane.ally
        left_lane.detected = False
        rightx = right_lane.allx
        righty = right_lane.ally
        right_lane.detected = False
    else:
        right_lane.allx = rightx
        right_lane.ally = righty

    # Fit a second order polynomial to each
    left_fit = np.polyfit(lefty, leftx, 2)
    right_fit = np.polyfit(righty, rightx, 2)
    # print(left_fit)

    # Sanity check
    if (left_lane.current_fit[0] == False):
        left_lane.current_fit = left_fit
        right_lane.current_fit = right_fit

    # print ("____")
    # print(abs(left_lane.current_fit[1] - left_fit[1]))
    if (abs(left_lane.current_fit[1] - left_fit[1]) > 0.18):

        left_lane.current_fit = left_lane.best_fit
        left_lane.detected = False
    else:
        left_lane.current_fit = left_fit
        left_lane.recent_xfitted.pop()
        left_lane.recent_xfitted.appendleft(left_lane.current_fit)
        avg = np.array([0, 0, 0], dtype='float')
        for element in left_lane.recent_xfitted:
            avg = avg + element
        left_lane.best_fit = avg / (len(left_lane.recent_xfitted))

    if (abs(right_lane.current_fit[1] - right_fit[1]) > 0.18):
        right_lane.current_fit = right_lane.best_fit
        right_lane.detected = False
    else:
        right_lane.current_fit = right_fit
        right_lane.recent_xfitted.pop()
        right_lane.recent_xfitted.appendleft(right_lane.current_fit)
        avg = np.array([0, 0, 0], dtype='float')
        for element in right_lane.recent_xfitted:
            avg = avg + element
        right_lane.best_fit = avg / (len(right_lane.recent_xfitted))

    if (abs(right_lane.current_fit[1] - right_fit[1]) > 0.38 and
            abs(left_lane.current_fit[1] - left_fit[1]) < 0.1):

        right_lane.current_fit[0] = left_lane.current_fit[0]
        right_lane.current_fit[1] = left_lane.current_fit[1]
        right_lane.current_fit[2] = left_lane.current_fit[2] + 600
        right_lane.recent_xfitted.pop()
        right_lane.recent_xfitted.appendleft(right_lane.current_fit)
        avg = np.array([0, 0, 0], dtype='float')
        for element in right_lane.recent_xfitted:
            avg = avg + element
        right_lane.best_fit = avg / (len(right_lane.recent_xfitted))

    if (abs(left_lane.current_fit[1] - left_fit[1]) > 0.38 and
            abs(right_lane.current_fit[1] - right_fit[1]) < 0.1):
        leftx = left_lane.allx
        lefty = left_lane.ally
        left_lane.detected = False
        rightx = right_lane.allx
        righty = right_lane.ally
        right_lane.detected = False
        # print("________________________________________")
        # cv2.waitKey(0)
        # какая то хрень, реагирует на сильные уходы линии за пределы видимости, а также моменты, когда линия вернулась
        left_lane.current_fit = left_fit
        left_lane.recent_xfitted.pop()
        left_lane.recent_xfitted.appendleft(left_lane.current_fit)
        avg = np.array([0, 0, 0], dtype='float')
        for element in left_lane.recent_xfitted:
            avg = avg + element
        left_lane.best_fit = avg / (len(left_lane.recent_xfitted))

    # Generate x and y values for plotting
    # ploty = np.linspace(0, 720-1, 720 )

    ploty = np.linspace(0, binary_warped.shape[0] - 1, binary_warped.shape[0])
    left_fitx = left_lane.current_fit[0] * ploty ** 2 + left_lane.current_fit[1] * ploty + left_lane.current_fit[2]
    right_fitx = right_lane.current_fit[0] * ploty ** 2 + right_lane.current_fit[1] * ploty + right_lane.current_fit[2]

    out_img[nonzeroy[left_lane_inds], nonzerox[left_lane_inds]] = [255, 0, 0]
    out_img[nonzeroy[right_lane_inds], nonzerox[right_lane_inds]] = [0, 0, 255]

    cv2.imshow("out2",out_img)

    return ploty, lefty, righty, leftx, rightx, left_fitx, right_fitx, out_img
