# slam-inspection-robot
# 基于RDK X5的多模态SLAM智能巡检机器人

本仓库为《基于RDK X5的多模态SLAM智能巡检机器人》项目的重点代码文件，主要包含多点巡检、YOLO人体检测、异常停车、Web监控、SLAM与Nav2配置、雷达与TF配置以及巡检地图文件。

## 项目简介

本项目基于 RDK X5、ROS2、YDLIDAR X3 激光雷达、IMX219-160IR 摄像头和 R550A_PLUS_diff_arm 移动底盘，设计并实现了一套面向室内场景的智能巡检机器人系统。

机器人能够通过激光雷达完成 SLAM 建图和 Nav2 自主导航，通过摄像头和 YOLOv8 完成人体目标检测。当巡检过程中检测到 person 类目标时，系统会自动取消当前导航任务、发布零速度停车、更新巡检状态，并通过 Web 页面显示实时画面和报警信息。

## 主要功能

- 基于 slam-toolbox 的二维 SLAM 建图
- 基于 Nav2 的目标点导航与多点自动巡检
- 基于 YOLOv8 的人体目标检测
- 检测到异常目标后自动停车
- 异常状态发布与日志记录
- Web 页面实时监控巡检画面和报警状态
- YDLIDAR X3 雷达方向与 TF 参数配置
- 巡检地图文件保存与加载

## 代码目录说明

```text
keycode/
├── startup/          启动脚本
├── nav/              多点巡检与异常停车程序
├── yolo/             YOLO人体检测状态节点
├── web/              Web监控程序
├── slam_nav_config/  SLAM与Nav2相关配置
├── lidar/            雷达与TF配置
└── map/              巡检地图文件
