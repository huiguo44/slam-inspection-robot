#!/bin/bash

echo "===== 启动最终多点安全巡检 ====="

source /opt/ros/humble/setup.bash
source /home/wheeltec/wheeltec_ros2/install/setup.bash

LOG_DIR=/home/wheeltec/demo_logs
mkdir -p $LOG_DIR

echo "先检查 Nav2 action server 是否存在..."
ros2 action list | grep navigate_to_pose

echo "先检查 /patrol/status 是否存在..."
ros2 topic list | grep patrol || true

echo ""
echo "确认你已经在 RViz 中完成："
echo "1. 2D Pose Estimate 初始位姿设置"
echo "2. /scan 点云与地图重合"
echo "3. 小车箭头方向与真实车头一致"
echo ""
echo "3 秒后启动 patrol_nav_node_final.py..."
sleep 3

python3 /home/wheeltec/patrol_nav_node_final.py 2>&1 | tee $LOG_DIR/patrol_final_$(date +%Y%m%d_%H%M%S).log
