#!/usr/bin/env python3

import os
#os.environ["CUDA_VISIBLE_DEVICES"]="-1" 
import tensorflow as tf

gpus = tf.config.experimental.list_physical_devices('GPU')

if gpus:
	try:
	# Currently, memory growth needs to be the same across GPUs
		for gpu in gpus:
			tf.config.experimental.set_memory_growth(gpu, True)
			logical_gpus = tf.config.experimental.list_logical_devices('GPU')
			print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
	except RuntimeError as e:
	# Memory growth must be set before GPUs have been initialized
		print(e)

from gazebo_msgs.srv import DeleteEntity
from gazebo_msgs.srv import SpawnEntity
from geometry_msgs.msg import Pose
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from std_srvs.srv import Empty
from geometry_msgs.msg import Twist

import json
import numpy as np
import random
import sys
import time
import math

from pic4rl.agents.ddpg_agent import DDPGLidarAgent
from pic4rl.agents.ddpg_visual_agent import DDPGVisualAgent
from pic4rl.agents.trainer import Pic4Trainer, Pic4VisualTrainer

from pic4rl.pic4rl_robots import MobileRobotState

from pic4rl.sensors.pic4rl_sensors_class import Sensors
from pic4rl.pic4rl_env import Pic4rl

from pic4rl.tasks.pic4rl_navigation_task import Pic4rlTask

from gym import spaces

import gym

class Pic4rlEnvironment(
    Pic4rlTask, 
    Pic4rl
    ):

    def __init__(self):
        Pic4rl.__init__(self)
        Pic4rlTask.__init__(self)
        #MobileRobotState.__init__(self)

class Pic4rlTraining():
    def __init__(self):
        #rclpy.logging.set_logger_level('pic4rl_training', 20)
        #rclpy.logging.set_logger_level('pic4rl_environment', 10)

        """************************************************************
        ** Initialise ROS publishers and subscribers
        ************************************************************"""
        qos = QoSProfile(depth=10)

        #self.env = Pic4rlEnvironment()
        #self.stage = int(stage)
	
        #self.avg_cmd_vel = [0.2,int(0)]
        #self.evalutate_Hz(init=True)

        # State size and action size
        self.state_size = 2 #goal distance, goal angle, lidar points
        self.action_size = 2 #linear velocity, angular velocity
        self.height = 60
        self.width = 80
        self.episode_size = 8000

        # Velocity limits and Controller freq
        self.max_linear_vel = 0.5
        self.max_angular_vel = 1.5
        self.control_freq = 10

        # Training parameters
        self.batch_size = 64
        self.train_start = 64
        #self.update_target_model_start = 128
        self.score_list = []

       # Load saved models
        self.load_model = False
        self.load_episode = 0


        #Instanciate DDPG Agent
        self.Agent = DDPGLidarAgent(state_size = self.state_size, action_size = self.action_size, 
             max_linear_vel = self.max_linear_vel, max_angular_vel= self.max_angular_vel, 
             max_memory_size = 200000, 
             load = self.load_model,
             gamma = 0.99, epsilon = 1.0, epsilon_decay = 0.998, epsilon_min = 0.05, 
             tau = 0.01, 
             batch_size = self.batch_size, 
             noise_std_dev = 0.2)  


        #self.Agent = DDPGVisualAgent(state_size = self.state_size, 
        #    image_height = self.height, image_width = self.width,
        #    action_size = self.action_size, 
        #    max_linear_vel = self.max_linear_vel, max_angular_vel= self.max_angular_vel, 
        #    max_memory_size = 150000, 
        #    load = self.load_model,
        #    gamma = 0.99, epsilon = 1.0, epsilon_decay = 0.998, epsilon_min = 0.05, 
        #    tau = 0.01, 
        #    batch_size = self.batch_size, 
        #    noise_std_dev = 0.2)  

        # Define and stat training process
        self.Trainer = Pic4Trainer(self.Agent, self.load_episode,\
                                    self.episode_size, self.train_start,\
                                    Pic4rlEnvironment)
        
        #self.Trainer = Pic4VisualTrainer(self.Agent, self.load_episode,\
        #                                 self.episode_size, self.train_start)
    def learn(self):
        self.Trainer.process()


def main(args=None):
    try:
        rclpy.init()
        pic4rl_training= Pic4rlTraining()
        pic4rl_training.learn()
    finally:
        pic4rl_training.Trainer.env.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()