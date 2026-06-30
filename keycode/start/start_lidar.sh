#!/bin/bash
export ROS_DOMAIN_ID=0
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
unset CYCLONEDDS_URI

source /opt/ros/humble/setup.bash
source /home/wheeltec/ydlidar_ws/install/setup.bash

ros2 launch ydlidar_ros2_driver ydlidar_launch.py
