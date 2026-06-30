#!/bin/bash
source /opt/ros/humble/setup.bash
source /home/wheeltec/wheeltec_ros2/install/setup.bash

ros2 launch wheeltec_nav2 wheeltec_nav2_model.launch.py
