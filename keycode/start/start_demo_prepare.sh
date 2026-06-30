#!/bin/bash

LOG_DIR=/home/wheeltec/demo_logs/$(date +%Y%m%d_%H%M%S)
mkdir -p $LOG_DIR

echo "===== 清理旧节点 ====="

timeout 3s /home/wheeltec/stop_robot.sh || true

pkill -9 -f patrol_nav_node_final.py
pkill -9 -f patrol_nav_node_safe.py
pkill -9 -f patrol_nav_node.py

pkill -9 -f yolo_patrol_node.py
pkill -9 -f patrol_web.py
pkill -9 -f compressed_to_raw.py
pkill -9 -f abnormal_snapshot_node.py

pkill -9 -f dnn_node_example
pkill -9 -f websocket

pkill -9 -f start_nav.sh
pkill -9 -f wheeltec_nav2
pkill -9 -f nav2
pkill -9 -f controller_server
pkill -9 -f planner_server
pkill -9 -f bt_navigator
pkill -9 -f amcl
pkill -9 -f map_server

pkill -9 -f start_lidar.sh
pkill -9 -f ydlidar
pkill -9 -f ydlidar_ros2_driver

pkill -9 -f start_base.sh
pkill -9 -f turn_on_wheeltec_robot
pkill -9 -f wheeltec_robot_node

sleep 2

echo "===== 启动底盘 ====="
setsid /home/wheeltec/start_base.sh > $LOG_DIR/base.log 2>&1 < /dev/null &
sleep 8

echo "===== 启动 YDLIDAR X3 ====="
setsid /home/wheeltec/start_lidar.sh > $LOG_DIR/lidar.log 2>&1 < /dev/null &
sleep 5

echo "===== 启动 Nav2 ====="
setsid /home/wheeltec/start_nav.sh > $LOG_DIR/nav.log 2>&1 < /dev/null &
sleep 15

echo "===== 启动 YOLOv8 检测 ====="
setsid bash -lc '
source /opt/tros/humble/setup.bash
export CAM_TYPE=mipi
ros2 launch dnn_node_example dnn_node_example.launch.py \
dnn_example_config_file:=config/yolov8workconfig.json \
dnn_example_image_width:=1920 \
dnn_example_image_height:=1080
' > $LOG_DIR/yolo.log 2>&1 < /dev/null &
sleep 10

echo "===== 启动 YOLO 巡检状态节点 ====="
setsid bash -lc '
source /opt/tros/humble/setup.bash
python3 /home/wheeltec/yolo_patrol_node.py
' > $LOG_DIR/yolo_patrol.log 2>&1 < /dev/null &
sleep 3

echo "===== 启动图像转换节点 compressed_to_raw.py ====="
setsid bash -lc '
source /opt/tros/humble/setup.bash
python3 /home/wheeltec/compressed_to_raw.py
' > $LOG_DIR/compressed_to_raw.log 2>&1 < /dev/null &
sleep 3

echo "===== 启动异常截图节点 ====="
setsid bash -lc '
source /opt/tros/humble/setup.bash
python3 /home/wheeltec/abnormal_snapshot_node.py
' > $LOG_DIR/abnormal_snapshot.log 2>&1 < /dev/null &
sleep 2

echo "===== 启动 Web 监控页面 ====="
setsid bash -lc '
source /opt/tros/humble/setup.bash
python3 /home/wheeltec/patrol_web.py
' > $LOG_DIR/patrol_web.log 2>&1 < /dev/null &
sleep 3

echo "===== 检查 Nav2 节点 ====="
source /opt/ros/humble/setup.bash
source /home/wheeltec/wheeltec_ros2/install/setup.bash

ros2 node list | grep -E "amcl|map_server|controller_server|planner_server|bt_navigator|costmap" || true

echo ""
echo "===== 启动完成，但还没有开始巡检 ====="
echo "日志目录：$LOG_DIR"
echo ""
echo "下一步请手动操作："
echo "1. 打开 RViz"
echo "2. 使用 2D Pose Estimate 设置小车初始位姿"
echo "3. 确认 /scan 点云和地图墙体重合"
echo "4. 确认 Web 页面正常"
echo "5. 然后运行：/home/wheeltec/start_patrol_final.sh"
echo ""
