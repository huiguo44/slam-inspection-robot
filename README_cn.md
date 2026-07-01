# 基于 RDK X5 的多模态 SLAM 智能巡检机器人

## 1. 项目简介

本项目基于 RDK X5 机器人开发平台，面向实验室、仓储通道、设备间、校园走廊等室内半结构化场景，设计并实现了一套多模态 SLAM 智能巡检机器人系统。

系统融合 YDLIDAR X3 激光雷达、IMX219-160IR 红外摄像头、ROS2、slam-toolbox、Nav2、YOLO 目标检测与 Web 监控等模块，实现了环境建图、自主导航、多点巡检、人体目标检测、异常停车、异常状态发布和网页端监控等功能。

项目整体流程如下：

```text
激光雷达 / 摄像头
        ↓
ROS2 感知与数据发布
        ↓
slam-toolbox 建图 + Nav2 定位导航
        ↓
多点自动巡检
        ↓
YOLO 人体检测
        ↓
异常停车 / 状态发布 / Web 监控
```

## 2. 功能特点

- **SLAM 建图**：通过 YDLIDAR X3 激光雷达采集环境信息，使用 slam-toolbox 构建二维栅格地图。
- **自主导航**：基于 Nav2 实现地图加载、AMCL 定位、路径规划和运动控制。
- **多点巡检**：通过巡检脚本按 A、B、C、D、E 等预设点位顺序发送导航目标，实现定点巡检。
- **YOLO 人体检测**：基于 RDK X5 的端侧推理能力，对摄像头画面中的 `person` 类目标进行检测。
- **异常停车联动**：巡检过程中检测到人员目标后，系统取消当前导航目标并发布零速度指令，使机器人停车。
- **状态恢复继续巡检**：人员离开后，状态恢复为 Normal，机器人继续执行未完成的巡检任务。
- **Web 监控**：通过浏览器查看实时画面、巡检状态、检测结果和异常信息。
- **模块化代码结构**：将雷达、地图、导航、SLAM、启动脚本、Web、YOLO 等关键代码按目录分类存放，便于复现和维护。

## 3. 硬件平台

| 模块 | 型号 / 名称 | 作用 |
|---|---|---|
| 主控平台 | RDK X5 | 运行 ROS2、TROS、YOLO、Nav2、Web 服务等上层程序 |
| 底盘平台 | R550A_PLUS_diff_arm | 移动机器人运动执行平台 |
| 底盘控制器 | STM32 控制器 | 接收 `/cmd_vel` 指令并驱动电机运动 |
| 激光雷达 | YDLIDAR X3 | 发布 `/scan` 数据，用于 SLAM 建图、定位和导航避障 |
| 摄像头 | IMX219-160IR 红外摄像头 | 采集巡检画面，用于 YOLO 检测和 Web 显示 |
| 显示与调试 | HDMI 屏幕 / PC / 手机浏览器 | RViz 调试、Web 监控和演示展示 |

## 4. 软件环境

| 软件 / 框架 | 说明 |
|---|---|
| Ubuntu 22.04 | RDK X5 系统环境 |
| ROS2 Humble | 机器人通信、导航、建图基础框架 |
| TROS | RDK X5 视觉算法与推理运行环境 |
| slam-toolbox | 二维 SLAM 建图 |
| Nav2 | AMCL 定位、路径规划、运动控制 |
| YDLIDAR ROS2 Driver | YDLIDAR X3 雷达驱动 |
| dnn_node_example / hobot_dnn | YOLO 目标检测推理 |
| OpenCV / cv_bridge | 图像处理与 ROS 图像转换 |
| Flask | Web 监控页面服务 |

## 5. 代码目录结构

本仓库的关键代码统一放在 `keycode` 目录下，目录结构如下：

```text
.
├── README_cn.md
├── README.MD
├── LICENSE
└── keycode
    ├── lidar
    │   ├── X3.yaml
    │   └── robot_model.yaml
    ├── map
    │   ├── patrol_map_v5.pgm
    │   └── patrol_map_v5.yaml
    ├── nav
    │   ├── patrol_nav_node.py
    │   ├── patrol_nav_node_final.py
    │   └── patrol_nav_node_safe.py
    ├── slam
    │   ├── WHEELTEC.yaml
    │   ├── param_R550A_PLUS_diff_arm.yaml
    │   └── safe_slam_launch.py
    ├── start
    │   ├── start_base.sh
    │   ├── start_demo_prepare.sh
    │   ├── start_lidar.sh
    │   ├── start_nav.sh
    │   ├── start_patrol_final.sh
    │   └── stop_robot.sh
    ├── web
    │   ├── compressed_to_raw.py
    │   └── patrol_web.py
    └── yolo
        └── yolo_patrol_node.py
```

## 6. 主要文件说明

### 6.1 `keycode/lidar`

| 文件 | 说明 |
|---|---|
| `X3.yaml` | YDLIDAR X3 激光雷达配置文件，包含串口、波特率、扫描方向等参数 |
| `robot_model.yaml` | 机器人模型与传感器坐标变换相关配置 |

### 6.2 `keycode/map`

| 文件 | 说明 |
|---|---|
| `patrol_map_v5.pgm` | 最终用于 Nav2 导航的二维栅格地图 |
| `patrol_map_v5.yaml` | 地图元信息文件，包含分辨率、原点、阈值等参数 |

### 6.3 `keycode/nav`

| 文件 | 说明 |
|---|---|
| `patrol_nav_node.py` | 基础多点巡检脚本 |
| `patrol_nav_node_safe.py` | 安全版多点巡检脚本，支持异常状态订阅和停车处理 |
| `patrol_nav_node_final.py` | 最终演示版巡检脚本，用于多点巡检与异常停车联动 |

### 6.4 `keycode/slam`

| 文件 | 说明 |
|---|---|
| `safe_slam_launch.py` | 安全版 SLAM 启动文件，仅启动 slam-toolbox，避免重复启动底盘和雷达 |
| `WHEELTEC.yaml` | Nav2 地图加载相关配置 |
| `param_R550A_PLUS_diff_arm.yaml` | R550A_PLUS_diff_arm 底盘对应的 Nav2 参数配置 |

### 6.5 `keycode/start`

| 文件 | 说明 |
|---|---|
| `start_base.sh` | 启动底盘通信节点 |
| `start_lidar.sh` | 启动 YDLIDAR X3 雷达节点 |
| `start_nav.sh` | 启动 Nav2 导航系统 |
| `start_demo_prepare.sh` | 最终演示准备脚本，启动底盘、雷达、Nav2、YOLO、Web 等基础模块 |
| `start_patrol_final.sh` | 在 RViz 设置初始位姿后，启动最终多点巡检脚本 |
| `stop_robot.sh` | 急停脚本，持续向 `/cmd_vel` 发布零速度 |

### 6.6 `keycode/web`

| 文件 | 说明 |
|---|---|
| `compressed_to_raw.py` | 图像格式转换节点，用于 Web 显示链路 |
| `patrol_web.py` | Flask Web 监控服务，显示实时图像、巡检状态和报警信息 |

### 6.7 `keycode/yolo`

| 文件 | 说明 |
|---|---|
| `yolo_patrol_node.py` | 订阅 YOLO 检测结果，判断 `person` 目标并发布 `/patrol/status` 状态 |

## 7. 部署说明

本仓库主要用于提交和复现关键代码。实际部署时，需要将对应文件放到 RDK X5 小车端运行环境中。建议先备份原始配置文件，再复制本仓库中的最终配置。

### 7.1 赋予脚本执行权限

```bash
chmod +x keycode/start/*.sh
chmod +x keycode/nav/*.py
chmod +x keycode/web/*.py
chmod +x keycode/yolo/*.py
chmod +x keycode/slam/*.py
```

### 7.2 推荐部署方式

如果脚本中使用的是 `/home/wheeltec/` 绝对路径，可将关键脚本复制到 `/home/wheeltec/` 目录：

```bash
cp keycode/start/*.sh /home/wheeltec/
cp keycode/nav/*.py /home/wheeltec/
cp keycode/web/*.py /home/wheeltec/
cp keycode/yolo/*.py /home/wheeltec/
cp keycode/slam/safe_slam_launch.py /home/wheeltec/
```

地图文件可复制到：

```bash
mkdir -p /home/wheeltec/maps
cp keycode/map/patrol_map_v5.* /home/wheeltec/maps/
```

涉及 `WHEELTEC.yaml`、`param_R550A_PLUS_diff_arm.yaml`、`X3.yaml`、`robot_model.yaml` 等配置文件时，请先备份原文件，再按实际路径替换。

## 8. 启动流程

### 8.1 最终演示流程

最终演示时，建议分两步启动：先启动底层功能，再设置初始位姿，最后启动巡检脚本。

#### 第一步：启动演示准备脚本

```bash
cd /home/wheeltec
chmod +x start_demo_prepare.sh
./start_demo_prepare.sh
```

该脚本用于启动底盘、雷达、Nav2、YOLO 检测、Web 服务等基础模块，但不会立即启动巡检任务。

#### 第二步：在 RViz 中设置初始位姿

打开 RViz 后，设置：

```text
Fixed Frame = map
Map Topic = /map
LaserScan Topic = /scan
```

使用 `2D Pose Estimate` 将机器人实际位置与地图对齐，并确认 `/scan` 点云与地图墙体重合。

#### 第三步：启动最终巡检脚本

```bash
cd /home/wheeltec
chmod +x start_patrol_final.sh
./start_patrol_final.sh
```

机器人将按照预设巡检点执行自动巡检任务。巡检过程中，如果 YOLO 检测到人员目标，机器人会取消当前 Nav2 目标并停车；当状态恢复后，继续执行后续巡检点。

### 8.2 单模块启动方式

如需单独调试，可以分别启动以下模块：

```bash
# 启动底盘
./start_base.sh

# 启动雷达
./start_lidar.sh

# 启动 Nav2
./start_nav.sh

# 急停
./stop_robot.sh
```

### 8.3 Web 监控访问

在浏览器中访问：

```text
http://<RDK_X5_IP>:5000
```

其中 `<RDK_X5_IP>` 替换为 RDK X5 的实际 IP 地址。

Web 页面可用于查看：

- 实时巡检画面
- YOLO 检测状态
- `/patrol/status` 巡检状态
- 异常报警信息
- 手动控制按钮

## 9. ROS2 关键话题

| 话题 | 类型 / 作用 |
|---|---|
| `/cmd_vel` | 底盘速度控制 |
| `/odom` | 里程计反馈 |
| `/imu` | IMU 姿态数据 |
| `/tf`、`/tf_static` | 坐标变换 |
| `/scan` | 激光雷达扫描数据 |
| `/map` | SLAM / Nav2 使用的地图 |
| `/image_raw` | 摄像头原始图像 |
| `/hobot_dnn_detection` | YOLO 检测结果 |
| `/patrol/status` | 巡检状态与异常状态 |
| `/web/image_raw` | Web 页面使用的图像流 |

## 10. 测试结果

项目已经完成以下功能验证：

- 底盘通信正常，机器人可响应 `/cmd_vel` 速度指令。
- YDLIDAR X3 激光雷达可正常发布 `/scan` 数据。
- slam-toolbox 可完成室内二维地图构建。
- Nav2 可加载地图并完成目标点导航。
- 多点巡检脚本可按预设点位完成 A → B → C → D → E 自动巡检。
- YOLO 检测节点可识别 `person` 类目标。
- 巡检过程中检测到人员后，机器人可取消导航目标并自动停车。
- 人员离开后，系统状态恢复，机器人可继续执行巡检任务。
- Web 页面可显示实时画面、巡检状态和异常信息。

## 11. 注意事项

1. 启动最终巡检前，必须先在 RViz 中使用 `2D Pose Estimate` 设置初始位姿。
2. 如果 `/scan` 点云与地图不重合，应先检查初始位姿、雷达方向和 TF 配置。
3. 测试 `/cmd_vel` 时不要只用 `Ctrl + C` 停止发布器，应主动发布零速度或运行 `stop_robot.sh`。
4. 替换 Nav2、雷达和机器人模型配置前，请先备份原文件。
5. 演示现场建议优先使用稳定网络，Web 展示可使用手机或电脑浏览器访问。

## 12. 开源协议

本项目建议使用 Apache License 2.0 开源协议。请查看仓库根目录下的 `LICENSE` 文件。
