#!/usr/bin/env python3
#
# MIT License

# Copyright (c) 2021 PIC4SeR
# Authors: Enrico Sutera (enricosutera), Mauro Martini(maurom3197)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

# General purpose
import time
import numpy as np
import random 
import math 
import os
from ament_index_python.packages import get_package_share_directory

# ROS related
import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from std_srvs.srv import Empty

from geometry_msgs.msg import Twist
from geometry_msgs.msg import Pose

from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry

from rclpy.qos import QoSProfile
from rclpy.qos import qos_profile_sensor_data

# others

from pic4rl.sensors.pic4rl_sensors import pose_2_xyyaw
from pic4rl.sensors.pic4rl_sensors import clean_laserscan, laserscan_2_list, laserscan_2_n_points_list

import gym
from gym import spaces


import collections

class WheeledRobot():
	def __init__(self):

		max_linear_x_speed = 0.3
		min_linear_x_speed = -0.3

		#max_linear_y_speed = 0.5
		#min_linear_y_speed = -0.5

		max_angular_z_speed = 1
		min_angular_z_speed = -1.0

		action =[
			[min_linear_x_speed, max_linear_x_speed],
			[min_angular_z_speed, max_angular_z_speed]
			#[-0.5, 0.5], # x_speed 
			##[-0.5, 0.5], # y_speed
			#[-1, 1] # theta_speed
		]


		low_action = []
		high_action = []
		for i in range(len(action)):
			low_action.append(action[i][0])
			high_action.append(action[i][1])

		low_action = np.array(low_action, dtype=np.float32)
		high_action = np.array(high_action, dtype=np.float32)

		self.action_space = spaces.Box(
			low=low_action,
			high=high_action,
			#shape=(1,),
			dtype=np.float32
		)
		
		"""
		state
		"""
		state =[

		[0., 5.], # goal_distance 
		[-math.pi, math.pi], # goal_angle
		#[-math.pi, math.pi] # yaw
		]
		

		low_state = []
		high_state = []
		for i in range(len(state)):
			low_state.append(state[i][0])
			high_state.append(state[i][1])

		self.low_state = np.array(low_state, dtype=np.float32)
		self.high_state = np.array(high_state, dtype=np.float32)

		self.observation_space = spaces.Box(
			low=self.low_state,
			high=self.high_state,
			dtype=np.float32
		)
