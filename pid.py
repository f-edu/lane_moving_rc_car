# -----------
# User Instructions
#
# Implement a P controller by running 100 iterations
# of robot motion. The desired trajectory for the
# robot is the x-axis. The steering angle should be set
# by the parameter tau so that:
#
# steering = -tau * crosstrack_error
#
# Note that tau is called "param" in the function
# below.
#
# Your code should print output that looks like
# the output shown in the video. That is, at each step:
# print myrobot, steering
#
# Only modify code at the bottom!
# ------------

import random
import numpy as np
# import matplotlib.pyplot as plt


# ------------------------------------------------
#
# this is the Robot class
#

class Robot(object):
    def __init__(self, length=20.0):
        """
        Creates robot and initializes location/orientation to 0, 0, 0.
        """
        self.x = 0.0
        self.y = 0.0
        self.prew_y = 0.0
        self.orientation = 0.0
        self.length = length
        self.steering_noise = 0.0
        self.distance_noise = 0.0
        self.steering_drift = 0.0

    def set(self, x, y, orientation):
        """
        Sets a robot coordinate.
        """
        self.x = x
        self.y = y
        self.orientation = orientation % (2.0 * np.pi)

    def set_noise(self, steering_noise, distance_noise):
        """
        Sets the noise parameters.
        """
        # makes it possible to change the noise parameters
        # this is often useful in particle filters
        self.steering_noise = steering_noise
        self.distance_noise = distance_noise

    def set_steering_drift(self, drift):
        """
        Sets the systematical steering drift parameter
        """
        self.steering_drift = drift

    def move(self, steering, distance, tolerance=0.001, max_steering_angle=np.pi / 24.0):
        """
        steering = front wheel steering angle, limited by max_steering_angle
        distance = total distance driven, most be non-negative
        """
        if steering > max_steering_angle:
            steering = max_steering_angle
        if steering < -max_steering_angle:
            steering = -max_steering_angle
        if distance < 0.0:
            distance = 0.0

        # make a new copy
        # res = Robot()
        # res.length = self.length
        # res.steering_noise = self.steering_noise
        # res.distance_noise = self.distance_noise
        # res.steering_drift = self.steering_drift

        # apply noise
        steering2 = random.gauss(steering, self.steering_noise)
        distance2 = random.gauss(distance, self.distance_noise)

        # apply steering drift
        steering2 += self.steering_drift
        # print(steering2)
        # Execute motion
        turn = np.tan(steering2) * distance2 / self.length
        # print("steering2: {}".format(steering2))
        if abs(turn) < tolerance:
            # approximate by straight line motion
            self.x += distance2 * np.cos(self.orientation)
            self.y += distance2 * np.sin(self.orientation)
            self.orientation = (self.orientation + turn) % (2.0 * np.pi)
        else:
            # approximate bicycle model for motion
            radius = distance2 / turn
            cx = self.x - (np.sin(self.orientation) * radius)
            cy = self.y + (np.cos(self.orientation) * radius)
            self.orientation = (self.orientation + turn) % (2.0 * np.pi)
            self.x = cx + (np.sin(self.orientation) * radius)
            self.y = cy - (np.cos(self.orientation) * radius)

    def __repr__(self):
        return '[x=%.5f y=%.5f orient=%.5f]' % (self.x, self.y, self.orientation)


############## ADD / MODIFY CODE BELOW ####################
# ------------------------------------------------------------------------
#
# run - does a single control run

def run_PID(robot, tau_p, tau_d, tau_i, n=1000, speed=1.0):
    x_trajectory = []
    y_trajectory = []
    # TODO: your code here
    cteSum = 0
    for i in range(n):
        if i == 0:
            cte_0 = 0
        else:
            cte_0 = cte
        cte = robot.y
        cteSum += cte
        steering = -tau_p * cte - tau_d * (cte - cte_0) - tau_i * cteSum

        robot.move(steering, speed)
        x_trajectory.append(robot.x)
        y_trajectory.append(robot.y)
    return x_trajectory, y_trajectory


def run_PID_once(robot, tau_p, tau_d, tau_i, speed=1.0):
    # TODO: your code here
    cteSum = 0

    cte_0 = robot.prew_y

    # print(cte_0)
    cte = robot.y

    # print(cte_0, cte)
    cteSum += cte
    steering = -tau_p * cte - tau_d * (cte - cte_0) - tau_i * cteSum
    # print(steering)
    # print("steering: {}".format(steering))

    robot.move(steering, speed)

    x_trajectory = robot.x
    y_trajectory = robot.y

    robot.prew_y = robot.y

    return x_trajectory, y_trajectory, steering

# robot = Robot()
# ## cte - 2 значение (y)
#
# robot.set_noise(np.pi/48, 0)
# robot.set_steering_drift(10.0/180*np.pi)


# robot.set(0, 5, 0)
# print(robot.y,robot.prew_y)
# x_t_PID, y_t_PID = run_PID_once(robot,0.3, 2, 0.004)
# print(y_t_PID)
#
# robot.set(0, 4.99, 0)
# print(robot.y,robot.prew_y)
# x2_t_PID, y2_t_PID = run_PID_once(robot,0.3, 2, 0.004)
# print(y2_t_PID)
#
# robot.set(0, 4.79, 0)
# print(robot.y,robot.prew_y)
# x3_t_PID, y3_t_PID = run_PID_once(robot,0.3, 2, 0.004)
# print(y3_t_PID)
#
#
# robot.set(0, 4.29, 0)
# print(robot.y,robot.prew_y)
# x4_t_PID, y4_t_PID = run_PID_once(robot,0.3, 2, 0.004)
# print(y4_t_PID)
#
# robot.set(0, 3.19, 0)
# print(robot.y,robot.prew_y)
# x5_t_PID, y5_t_PID = run_PID_once(robot,0.3, 2, 0.004)
# print(y5_t_PID)
#
# robot.set(0, 1.79, 0)
# print(robot.y,robot.prew_y)
# x6_t_PID, y6_t_PID = run_PID_once(robot,0.3, 2, 0.004)
# print(y6_t_PID)

# i=i+1
# print (y_t_PID)

# n = len(x_t_PID)
#
# plt.plot(x_t_PID, y_t_PID, 'b', label='PID controller')
# plt.plot(x_t_PID, np.zeros(n), 'r', label='reference')
# plt.legend(loc='upper left')
# plt.show()

# plt.savefig('../PID.png',dpi=400)



