# 基于 RDK X5 的多模态 SLAM 智能巡检机器人

## 1. 项目简介

本项目基于 **RDK X5** 机器人开发平台，设计并实现了一套面向室内半结构化场景的多模态 SLAM 智能巡检机器人系统。系统融合 **激光雷达、红外摄像头、ROS2、slam-toolbox、Nav2、YOLOv8 目标检测和 Web 监控** 等模块，实现了从环境感知、地图构建、自主定位、路径规划、运动执行到异常识别与远程反馈的完整闭环。

机器人可在实验室、仓储通道、设备间、校园走廊、小型办公区域等室内环境中执行巡检任务。系统支持激光雷达 SLAM 建图、Nav2 多点自动巡检、YOLO 人体检测、检测到人员后自动停车、异常状态发布、异常日志记录以及浏览器端实时监控等功能。

## 2. 功能特性

- **SLAM 建图**：基于 YDLIDAR X3 激光雷达和 slam-toolbox 构建二维栅格地图。
- **自主导航**：基于 Nav2 实现地图加载、AMCL 定位、路径规划和运动控制。
- **多点巡检**：支持按照预设 A、B、C、D、E 巡检点顺序执行自动巡检任务。
- **视觉感知**：通过 IMX219-160IR 红外摄像头采集巡检画面，支持普通光照和弱光场景图像输入。
- **人体检测**：基于 YOLOv8 检测画面中的 `person` 类目标。
- **异常停车**：巡检过程中检测到人员后，系统自动取消当前导航目标并发布零速度指令停车。
- **异常恢复**：当人员离开、状态恢复正常后，机器人可继续执行未完成的巡检任务。
- **Web 监控**：浏览器端显示实时画面、检测状态、异常信息和巡检状态。
- **异常记录**：支持异常事件日志记录，便于后续查看和分析。

## 3. 系统组成

### 3.1 硬件组成

| 模块 | 型号 / 名称 | 作用 |
|---|---|---|
| 主控平台 | RDK X5 | 运行 ROS2、TROS、YOLO、Nav2、Web 服务等上层程序 |
| 运动底盘 | R550A_PLUS_diff_arm | 承载机器人运动平台 |
| 底盘控制器 | STM32 控制器 | 接收速度指令并控制电机运动 |
| 激光雷达 | YDLIDAR X3 | 获取环境距离信息，用于 SLAM 建图和导航避障 |
| 摄像头 | IMX219-160IR 红外摄像头 | 采集巡检画面，用于人体检测和 Web 显示 |
| 显示 / 交互 | HDMI 屏幕、浏览器终端 | 用于 RViz 调试和 Web 监控 |
| 电源模块 | 底盘电池 / 稳压供电 | 为底盘、主控和传感器供电 |

### 3.2 软件组成

| 软件 / 功能包 | 作用 |
|---|---|
| ROS2 Humble | 机器人通信和节点管理框架 |
| TROS Humble | RDK X5 上的视觉推理和图像处理环境 |
| turn_on_wheeltec_robot | 底盘通信与运动控制 |
| ydlidar_ros2_driver | YDLIDAR X3 激光雷达驱动 |
| slam-toolbox | 二维 SLAM 建图 |
| Nav2 | 地图加载、AMCL 定位、路径规划和运动控制 |
| hobot_dnn / dnn_node_example | YOLO 目标检测推理 |
| Flask / Web 服务 | 浏览器端实时监控和状态显示 |
| 自定义巡检节点 | 多点巡检、异常停车、状态联动 |

## 4. 系统架构

系统整体采用 ROS2 分布式架构，各模块通过 ROS2 话题、Action、TF 坐标变换和 Web 服务进行通信。

```text
YDLIDAR X3 激光雷达
        ↓ /scan
slam-toolbox / Nav2
        ↓
地图构建、AMCL 定位、路径规划
        ↓ /cmd_vel
STM32 底盘控制器 → 电机执行

IMX219-160IR 摄像头
        ↓ /image_raw
YOLOv8 人体检测
        ↓ /hobot_dnn_detection
异常判断节点
        ↓ /patrol/status
巡检控制节点 / Web 监控页面
        ↓
异常停车、日志记录、状态显示
```

## 5. 主要 ROS2 话题

| 话题名称 | 消息类型 | 作用 |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | 底盘速度控制 |
| `/odom` | `nav_msgs/msg/Odometry` | 里程计反馈 |
| `/imu` | `sensor_msgs/msg/Imu` | IMU 姿态数据 |
| `/tf`、`/tf_static` | `tf2_msgs/msg/TFMessage` | 坐标变换 |
| `/scan` | `sensor_msgs/msg/LaserScan` | 激光雷达扫描数据 |
| `/map` | `nav_msgs/msg/OccupancyGrid` | SLAM 或 Nav2 地图 |
| `/image_raw` | `sensor_msgs/msg/Image` | 摄像头原始图像 |
| `/hobot_dnn_detection` | `ai_msgs/msg/PerceptionTargets` | YOLO 检测结果 |
| `/patrol/status` | `std_msgs/msg/String` | 巡检状态 / 异常状态 |

## 6. 仓库目录结构

```text
.
├── README_cn.md
├── README.MD
├── LICENSE
├── scripts/
│   ├── start_demo_prepare.sh       # 启动底盘、雷达、Nav2、YOLO、Web 等准备程序
│   ├── start_patrol_final.sh       # 设置初始位姿后启动最终巡检
│   ├── patrol_nav_node_final.py    # 多点巡检与异常停车联动节点
│   ├── yolo_patrol_node.py         # YOLO 人体检测状态处理节点
│   ├── patrol_web.py               # Web 监控页面服务
│   ├── compressed_to_raw.py        # 图像格式转换节点
│   └── safe_slam_launch.py         # 安全版 SLAM 启动文件
├── config/
│   ├── WHEELTEC.yaml               # Nav2 地图配置文件
│   └── robot_model.yaml            # 机器人模型与传感器参数配置
├── maps/
│   ├── patrol_map_v5.yaml          # 巡检地图配置
│   └── patrol_map_v5.pgm           # 巡检地图图像
├── docs/
│   ├── system_architecture.png     # 系统架构图
│   ├── ros2_topics.png             # ROS2 话题通信图
│   └── hardware_connection.png     # 硬件连接示意图
└── images/
    ├── robot.jpg                   # 机器人实物图
    ├── slam.png                    # SLAM 建图效果
    ├── nav.png                     # Nav2 巡检效果
    ├── yolo.png                    # YOLO 检测效果
    └── web.png                     # Web 监控页面
```

> 注：实际仓库目录可根据代码整理情况调整，运行时请以实际文件路径为准。

## 7. 环境准备

### 7.1 基础环境

- RDK X5
- Ubuntu 22.04
- ROS2 Humble
- TROS Humble
- Python 3
- OpenCV
- Flask
- Nav2
- slam-toolbox
- ydlidar_ros2_driver
- hobot_dnn / dnn_node_example

### 7.2 设备连接检查

检查底盘控制器串口：

```bash
ls -l /dev/wheeltec_controller
```

正常情况下，底盘控制器会被识别为类似：

```text
/dev/wheeltec_controller -> ttyACM0
```

检查激光雷达串口：

```bash
ls -l /dev/ttyUSB*
```

YDLIDAR X3 通常为：

```text
/dev/ttyUSB0
```

## 8. 快速启动

本项目最终演示流程分为两个阶段：

1. **准备阶段**：启动底盘、雷达、Nav2、YOLO、Web，但不立刻开始巡检。
2. **巡检阶段**：在 RViz 中完成 2D Pose Estimate 初始位姿设置后，再启动多点巡检。

### 8.1 启动准备程序

在 RDK X5 终端执行：

```bash
cd /home/wheeltec
bash start_demo_prepare.sh
```

该脚本主要启动：

```text
底盘控制节点
YDLIDAR X3 雷达节点
Nav2 导航系统
YOLO 人体检测节点
巡检状态节点
Web 监控服务
```

### 8.2 设置初始位姿

打开 RViz：

```bash
source /opt/ros/humble/setup.bash
source /home/wheeltec/wheeltec_ros2/install/setup.bash
rviz2
```

在 RViz 中设置：

```text
Fixed Frame: map
Map Topic: /map
LaserScan Topic: /scan
TF: Enable
RobotModel: Enable
```

使用 **2D Pose Estimate** 在地图上设置机器人初始位置和朝向，使 `/scan` 点云与地图墙体基本重合。

### 8.3 启动最终巡检

初始位姿设置完成后，在 RDK X5 终端执行：

```bash
cd /home/wheeltec
bash start_patrol_final.sh
```

机器人将按照预设巡检点执行：

```text
A → B → C → D → E
```

巡检过程中，如果 YOLO 检测到 `person` 类目标，系统会自动取消当前 Nav2 导航目标并停车；当状态恢复正常后，机器人继续执行未完成的巡检点。

## 9. SLAM 建图流程

如需重新建图，可按以下流程执行。

### 9.1 启动底盘

```bash
setsid /home/wheeltec/start_base.sh > /home/wheeltec/base.log 2>&1 < /dev/null &
```

### 9.2 启动雷达

```bash
setsid /home/wheeltec/start_lidar.sh > /home/wheeltec/lidar.log 2>&1 < /dev/null &
```

### 9.3 启动安全版 SLAM

```bash
source /opt/ros/humble/setup.bash
source /home/wheeltec/wheeltec_ros2/install/setup.bash
ros2 launch /home/wheeltec/safe_slam_launch.py
```

### 9.4 保存地图

```bash
ros2 run nav2_map_server map_saver_cli -f /home/wheeltec/maps/patrol_map_v5
```

保存后会生成：

```text
patrol_map_v5.yaml
patrol_map_v5.pgm
```

## 10. Web 监控

启动 Web 服务后，可在同一局域网设备浏览器访问：

```text
http://<RDK_X5_IP>:5000
```

Web 页面可显示：

- 实时巡检画面
- YOLO 检测状态
- `Normal` / `Person Detected` 巡检状态
- 异常日志或报警截图
- 基础控制按钮

## 11. 异常处理逻辑

系统异常处理流程如下：

```text
摄像头采集图像
        ↓
YOLOv8 检测 person 类目标
        ↓
发布 /patrol/status = Person Detected
        ↓
巡检节点收到异常状态
        ↓
取消当前 Nav2 导航目标
        ↓
持续发布 /cmd_vel = 0
        ↓
机器人停车并等待状态恢复
        ↓
状态恢复 Normal 后继续巡检
```

## 12. 演示效果

系统已完成以下功能测试：

| 测试项目 | 实现情况 |
|---|---|
| 底盘运动控制 | 已实现 |
| 雷达扫描与点云显示 | 已实现 |
| slam-toolbox 建图 | 已实现 |
| Nav2 单点导航 | 已实现 |
| Nav2 多点巡检 | 已实现 |
| YOLO 人体检测 | 已实现 |
| 检测到人自动停车 | 已实现 |
| 人离开后继续巡检 | 已实现 |
| Web 实时监控 | 已实现 |
| 异常日志记录 | 已实现 |

## 13. 注意事项

1. 启动 Nav2 后，需要先在 RViz 中使用 **2D Pose Estimate** 设置初始位姿，再启动最终巡检脚本。
2. `/scan` 点云必须与地图墙体基本重合，否则导航可能失败。
3. 测试 `/cmd_vel` 后必须主动发布零速度，不能只依靠 `Ctrl+C` 停止发布器。
4. 雷达方向参数、`base_to_laser`、地图文件和 Nav2 参数已调试完成后，不建议随意修改。
5. 若检测到人后小车未停车，需要检查巡检脚本是否订阅 `/patrol/status`，并确认是否取消了当前 Nav2 目标。
6. 建图和导航建议使用同一套雷达参数和 TF 配置，避免旧地图与当前传感器方向不一致。
7. 比赛演示时建议先运行准备脚本，确认 Web 页面和 RViz 定位正常后，再启动巡检脚本。

## 14. 项目适用场景

本项目适用于室内半结构化场景下的智能巡检任务，例如：

- 实验室巡检
- 仓储通道巡检
- 设备间巡检
- 机房巡检
- 教学楼走廊巡检
- 小型办公区域巡检

## 15. 后续优化方向

后续可从以下方向继续优化：

- 增加更多异常类型识别，例如火焰、烟雾、跌倒、未佩戴安全帽等。
- 优化 Web 页面交互，实现巡检任务配置和远程启动停止。
- 增加异常截图自动上传和历史记录查询功能。
- 引入语义地图，实现不同区域的任务化巡检。
- 优化弱光环境下的检测效果，提高夜间巡检稳定性。
- 增加电量检测和自动返航充电功能。

## 16. 许可证

本项目建议采用 Apache-2.0 License 开源协议。具体以仓库中的 `LICENSE` 文件为准。

## 17. 致谢

本项目基于 RDK X5、ROS2、Nav2、slam-toolbox、YDLIDAR 驱动、YOLO 目标检测等开源与平台工具完成，在此对相关开源社区和开发者表示感谢。
