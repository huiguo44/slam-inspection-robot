#!/bin/bash
export ROS_DOMAIN_ID=0
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
unset CYCLONEDDS_URI

source /opt/ros/humble/setup.bash
source /home/wheeltec/wheeltec_ros2/install/setup.bash

ros2 launch turn_on_wheeltec_robot turn_on_wheeltec_robot.launch.py
