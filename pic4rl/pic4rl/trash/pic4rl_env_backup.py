#!/usr/bin/env python3

"""
This class is to be inherited by all the pic4rl enviornments  
"""

import rclpy
from rclpy.node import Node
import random

from gazebo_msgs.srv import DeleteEntity, SpawnEntity
from std_srvs.srv import Empty

import numpy as np
import time 

from rclpy.executors import MultiThreadedExecutor

import pic4rl.pic4rl_utils
from pic4rl.pic4rl_utils import SpinWithTimeout
from pic4rl.pic4rl_utils import Differential2Twist

import pic4rl.pic4rl_services
from pic4rl.pic4rl_services import ResetWorldService, PauseService , UnpauseService
		
import pic4rl.pic4rl_sensors
from pic4rl.pic4rl_sensors import OdomSensor, pose_2_xyyaw
from pic4rl.pic4rl_sensors import CmdVelInfo
from pic4rl.pic4rl_sensors import LaserScanSensor, clean_laserscan, laserscan_2_list, laserscan_2_n_points_list
from pic4rl.pic4rl_sensors import MobileRobotState
from pic4rl.pic4rl_sensors import s7b3State

from pic4rl.pic4rl_sensors_class import Sensors

class Pic4rl(Sensors, MobileRobotState, Node):
	def __init__(self):
		Node.__init__(self, node_name ="pic4rl")
		rclpy.logging.set_logger_level('pic4rl', 10)
		Sensors.__init__(self, 
						generic_laser_scan_sensor = True,
						odometry_sensor = True)
		MobileRobotState.__init__(self)

		#super(Sensors,self).__init__(GeneralLidar = True)
		#self.state = MobileRobotState()

		self.initialization()



	"""###########
	# TOP LEVEL
	###########"""

	def initialization(self,args=None):
		self.get_logger().debug('[0] Initialization ...')
		self.initialize_ros()
		self.initialize_gazebo_services()
		self.initialize_sensors()

	def reset(self,args=None):
		self.get_logger().debug('[0] reset ...')
		self.reset_gazebo()
		self.collect_data_by_spinning(0.25)
		self.raw_data_to_state()

	def step(self,action):
		self.get_logger().debug('[0] step ...')
		self.send_action_to_Gazebo(action)
		self.collect_data_by_spinning()
		self.raw_data_to_state()
		self.get_observation()
		self.get_reward()

	"""#
	# -1
	#"""

	# INITIALIZATION

	def initialize_ros(self,args=None):
		self.get_logger().debug('	[1] initialize_ros ...')
		# Add spin_with_timeout function
		SpinWithTimeout(self)

	def initialize_gazebo_services(self,args=None):
		self.get_logger().debug('	[1] initialize_gazebo_services ...')
		ResetWorldService(self)
		PauseService(self)
		self.pause() # So that the simulation start paused
		UnpauseService(self)

		Differential2Twist(self)

	# rather robot
	def initialize_sensors(self,args=None):
		self.get_logger().debug('	[1] initialize_sensors ...')
	# RESET

	# Reset Gazebo
	def reset_gazebo(self,args=None):
		self.get_logger().debug('	[1] reset_gazebo ...')
		self.reset_world()
		#To be separated from
		self.goal_pos_x = random.uniform(-3,3)
		self.goal_pos_y = random.uniform(-3,3)

		# reset other elements if any

	# Collect data by node spinning
	def collect_data_by_spinning(self, timeout_sec = 0.1):
		self.get_logger().debug('	[1] collect_data_by_spinning ...')
		self.unpause()
		self.spin_with_timeout(timeout_sec)
		self.pause()

	# Get new state from gazebo 
	def raw_data_to_state(self,args=None):
		# TO DO:
		# there should be an history
		self.get_logger().debug('	[1]  raw_data_to_state ...')
		# inherited from MobileRobotState
		self.update_state()
		

	# Process state and obtain observation
	def get_observation(self,args=None):
		self.get_logger().debug('	[1]  get_observation ...')
		# inherited from MobileRobotState
		self.update_observation()
		# inherited from MobileRobotState
		return self.observation[-1] #from deque with len 2

	# STEP

	# Convert action to Twist(or other) msg and send to gazebo
	def send_action_to_Gazebo(self,action):
		self.get_logger().debug('	[1] send_action_to_Gazebo ...')
		self.send_cmd_command(action[0],action[1])


	# Collect data by node spinning
	# See in RESET

	# Process state and obtain observation
	# See in RESET

	# Compute reward from state (history)
	def get_reward(self,args=None):
		self.get_logger().debug('	[1] get_reward ...')
		self.compute_reward()
		

      
def main(args=None):
	rclpy.init()
	pic4rl = Pic4rl()
	#	rclpy.spin()

	pic4rl.get_logger().info('Node spinning once...')
	#rclpy.spin_once(pic4rl)
	try:
		for i in range(3):
			pic4rl.reset()
			for i in range(20):
				pic4rl.step([0.4,0.0])
				#print(type(pic4rl.odom_sensor.data))
				#print(type(pic4rl.cmd_vel_sensor.data))
				time.sleep(0.1)
			time.sleep(5)
			#pic4rl.spin_with_timeout()
			#pic4rl.send_cmd_command(1.0,1.0)
	finally:
		pic4rl.destroy_node()
		rclpy.shutdown()

if __name__ == '__main__':
	main()
