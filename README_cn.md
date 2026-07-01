# 基于 RDK X5 的多模态 SLAM 智能巡检机器人

## 1. 项目简介

本项目基于 **RDK X5** 机器人开发平台，面向实验室、仓储通道、设备间、校园走廊等室内半结构化场景，设计并实现了一套融合 **激光雷达、视觉感知、SLAM 建图、Nav2 自主导航、YOLO 人体检测、异常停车与 Web 监控** 的智能巡检机器人系统。

系统以 ROS2 为核心通信框架，利用 **YDLIDAR X3 激光雷达** 完成二维环境感知与 SLAM 建图，结合 **AMCL 定位与 Nav2 导航框架** 实现目标点导航和多点巡检；同时通过 **IMX219-160IR 红外摄像头** 采集巡检画面，并基于 YOLO 目标检测结果识别 `person` 类目标。当机器人在巡检过程中检测到人员目标时，系统会发布异常状态、取消当前导航目标、主动停车，并在人员离开后继续执行后续巡检任务。项目同时提供 Web 页面，用于展示实时画面、巡检状态、报警信息和基础控制按钮。

本项目实现了从 **环境感知 → 地图构建 → 路径规划 → 运动执行 → 异常识别 → 停车反馈 → Web 展示** 的完整闭环。

---

## 2. 功能特性

- **SLAM 建图**：基于 YDLIDAR X3 和 slam-toolbox 构建室内二维栅格地图。
- **地图导航**：基于 Nav2 实现 AMCL 定位、路径规划、局部避障和运动控制。
- **多点巡检**：通过巡检脚本自动发送 A、B、C、D、E 等目标点，按顺序完成定点巡检。
- **YOLO 人体检测**：订阅地瓜机器人 YOLO 示例输出的 `/hobot_dnn_detection`，识别 `person` 类目标。
- **异常停车联动**：检测到人员后，巡检脚本取消当前 Nav2 目标，持续发布零速度指令实现安全停车。
- **异常解除续航**：当 `/patrol/status` 恢复为 `Normal` 后，机器人继续执行未完成的巡检点。
- **Web 监控页面**：通过浏览器查看实时画面、检测状态、报警信息和基础控制按钮。
- **演示流程脚本化**：提供一键准备脚本和最终巡检启动脚本，便于比赛展示和复现实验。

---

## 3. 硬件平台

| 模块 | 型号 / 说明 |
|---|---|
| 主控平台 | RDK X5 |
| 移动底盘 | WHEELTEC R550A_PLUS_diff_arm |
| 底盘控制器 | STM32 底盘控制板 |
| 激光雷达 | YDLIDAR X3 |
| 摄像头 | IMX219-160IR 红外摄像头 |
| 通信方式 | ROS2 话题通信、串口通信、HTTP/Web 页面 |
| 主要执行话题 | `/cmd_vel` |
| 主要雷达话题 | `/scan` |
| 主要检测话题 | `/hobot_dnn_detection` |
| 巡检状态话题 | `/patrol/status` |

---

## 4. 软件环境

本项目基于以下环境开发和测试：

| 软件 / 框架 | 说明 |
|---|---|
| Ubuntu 22.04 | RDK X5 系统环境 |
| ROS2 Humble | 机器人通信与控制框架 |
| TROS Humble | RDK X5 视觉与 AI 推理环境 |
| slam-toolbox | 二维 SLAM 建图 |
| Nav2 | 地图加载、AMCL 定位、路径规划和导航控制 |
| ydlidar_ros2_driver | YDLIDAR X3 雷达驱动 |
| hobot_dnn / dnn_node_example | YOLO 目标检测示例 |
| Flask / OpenCV | Web 页面与图像流处理 |

> 注意：本仓库主要整理项目应用脚本、地图和关键配置文件，运行前需要 RDK X5 上已经安装好 ROS2、TROS、WHEELTEC 底盘功能包、YDLIDAR 驱动、Nav2、slam-toolbox 以及地瓜机器人 YOLO 示例相关依赖。

---

## 5. 项目目录结构

当前仓库代码目录如下：

```text
.
├── keycode/
│   └── 键盘控制或调试相关代码
│
├── lidar/
│   ├── X3.yaml
│   └── robot_model.yaml
│
├── map/
│   ├── patrol_map_v5.pgm
│   └── patrol_map_v5.yaml
│
├── nav/
│   ├── patrol_nav_node.py
│   ├── patrol_nav_node_final.py
│   └── patrol_nav_node_safe.py
│
├── slam/
│   ├── WHEELTEC.yaml
│   ├── param_R550A_PLUS_diff_arm.yaml
│   └── safe_slam_launch.py
│
├── start/
│   ├── start_base.sh
│   ├── start_demo_prepare.sh
│   ├── start_lidar.sh
│   ├── start_nav.sh
│   ├── start_patrol_final.sh
│   └── stop_robot.sh
│
├── web/
│   ├── compressed_to_raw.py
│   └── patrol_web.py
│
└── yolo/
    └── yolo_patrol_node.py
```

---

## 6. 目录说明

### 6.1 `keycode/`

用于存放键盘控制、小车调试或辅助控制相关代码。该目录主要用于开发和调试阶段。

### 6.2 `lidar/`

用于存放激光雷达和机器人模型相关配置。

- `X3.yaml`：YDLIDAR X3 雷达驱动参数配置文件。
- `robot_model.yaml`：机器人模型和传感器 TF 相关配置文件。

本项目在调试过程中对雷达方向进行了校正，确保 `/scan` 点云的前后、左右方向与真实车体坐标一致。

### 6.3 `map/`

用于存放最终导航使用的地图文件。

- `patrol_map_v5.pgm`：SLAM 建图生成的二维栅格地图图像。
- `patrol_map_v5.yaml`：地图参数文件，包括分辨率、原点、阈值等信息。

`patrol_map_v5` 是在雷达方向校正后重新构建的地图，用于 Nav2 定位和多点巡检。

### 6.4 `nav/`

用于存放多点巡检导航脚本。

- `patrol_nav_node.py`：基础多点巡检脚本。
- `patrol_nav_node_safe.py`：安全版多点巡检脚本，支持订阅 `/patrol/status` 并在异常时停车。
- `patrol_nav_node_final.py`：最终演示版巡检脚本，用于比赛展示流程。

最终版巡检逻辑为：

```text
发送巡检点目标
↓
Nav2 接受目标并导航
↓
如果检测到 Person Detected
↓
取消当前导航目标
↓
发布 0 速度停车
↓
等待状态恢复 Normal
↓
继续当前或下一个巡检点
```

### 6.5 `slam/`

用于存放 SLAM 和 Nav2 相关配置。

- `safe_slam_launch.py`：安全版 SLAM 启动文件，只启动 slam-toolbox，避免重复启动底盘和雷达导致串口冲突。
- `WHEELTEC.yaml`：Nav2 使用的地图配置文件。
- `param_R550A_PLUS_diff_arm.yaml`：适配 R550A_PLUS_diff_arm 底盘的 Nav2 参数配置文件。

### 6.6 `start/`

用于存放演示流程启动脚本。

- `start_base.sh`：启动底盘控制节点。
- `start_lidar.sh`：启动 YDLIDAR X3 雷达节点。
- `start_nav.sh`：启动 Nav2 导航系统。
- `start_demo_prepare.sh`：启动最终演示所需的底盘、雷达、Nav2、YOLO、Web 等基础模块，但不立即启动巡检。
- `start_patrol_final.sh`：在 RViz 中完成 2D Pose Estimate 后，启动最终巡检脚本。
- `stop_robot.sh`：主动向 `/cmd_vel` 发布零速度，用于急停和测试结束停车。

### 6.7 `web/`

用于存放 Web 监控相关代码。

- `compressed_to_raw.py`：用于图像话题格式转换，便于 Web 页面获取实时画面。
- `patrol_web.py`：Flask Web 服务程序，用于显示实时画面、巡检状态、报警信息和基础控制按钮。

### 6.8 `yolo/`

用于存放 YOLO 巡检状态处理代码。

- `yolo_patrol_node.py`：订阅 `/hobot_dnn_detection`，判断是否检测到 `person` 类目标，并发布 `/patrol/status` 状态信息。

---

## 7. 快速启动流程

> 以下流程适用于项目已经部署到 RDK X5，并且相关 ROS2/TROS/WHEELTEC 环境已经配置完成的情况。

### 7.1 赋予脚本执行权限

进入仓库根目录后执行：

```bash
chmod +x start/*.sh
chmod +x nav/*.py
chmod +x web/*.py
chmod +x yolo/*.py
```

### 7.2 启动演示准备环境

运行：

```bash
bash start/start_demo_prepare.sh
```

该脚本会启动：

```text
底盘控制
YDLIDAR X3 雷达
Nav2 导航
YOLO 人体检测
巡检状态节点
Web 监控服务
图像转换节点
```

此时机器人还不会自动开始巡检。

### 7.3 设置初始位姿

打开 RViz，加载地图并显示 `/scan` 点云，然后使用：

```text
2D Pose Estimate
```

在地图中设置机器人初始位置和朝向。确认 `/scan` 点云与地图墙体基本重合后，再启动巡检。

### 7.4 启动最终巡检

运行：

```bash
bash start/start_patrol_final.sh
```

机器人会按照预设巡检点执行多点巡检任务。

---

## 8. 单模块启动方式

如果需要分模块调试，可以按以下方式启动。

### 8.1 启动底盘

```bash
bash start/start_base.sh
```

### 8.2 启动雷达

```bash
bash start/start_lidar.sh
```

### 8.3 启动 Nav2

```bash
bash start/start_nav.sh
```

### 8.4 启动最终巡检脚本

```bash
python3 nav/patrol_nav_node_final.py
```

### 8.5 启动 YOLO 巡检状态节点

```bash
python3 yolo/yolo_patrol_node.py
```

### 8.6 启动 Web 页面

```bash
python3 web/patrol_web.py
```

### 8.7 急停机器人

```bash
bash start/stop_robot.sh
```

---

## 9. 建图流程

如需重新建图，可按以下流程操作：

```text
1. 启动底盘
2. 启动雷达
3. 启动 safe_slam_launch.py
4. 打开 RViz 查看 /map、/scan、TF
5. 使用键盘控制或低速移动小车完成建图
6. 保存地图为 .pgm 和 .yaml
7. 将新地图文件复制到 map/ 目录，并同步修改 Nav2 地图配置
```

本项目提供的 `slam/safe_slam_launch.py` 是安全版 SLAM 启动文件，主要作用是避免 WHEELTEC 原版一键建图 launch 重复启动底盘和雷达，导致串口冲突或节点冲突。

---

## 10. Web 访问说明

Web 页面用于展示巡检状态和实时画面。启动 `patrol_web.py` 后，可在同一局域网内使用浏览器访问：

```text
http://<RDK_X5_IP>:5000
```

页面可展示内容包括：

```text
实时巡检画面
YOLO 检测状态
Normal / Person Detected 巡检状态
异常报警信息
基础运动控制按钮
```

---

## 11. 关键话题说明

| 话题名称 | 消息类型 | 作用 |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | 底盘速度控制 |
| `/scan` | `sensor_msgs/msg/LaserScan` | 激光雷达扫描数据 |
| `/map` | `nav_msgs/msg/OccupancyGrid` | SLAM / Nav2 使用的地图 |
| `/tf` | `tf2_msgs/msg/TFMessage` | 坐标变换 |
| `/odom` | `nav_msgs/msg/Odometry` | 里程计数据 |
| `/hobot_dnn_detection` | `ai_msgs/msg/PerceptionTargets` | YOLO 检测结果 |
| `/patrol/status` | `std_msgs/msg/String` | 巡检状态，包含 Normal / Person Detected 等 |

---

## 12. 安全注意事项

1. 启动巡检前必须确认地图、初始位姿和雷达点云方向正确。
2. Nav2 巡检前必须先在 RViz 中完成 2D Pose Estimate。
3. 测试运动控制时不要只按 `Ctrl+C` 停止发布速度，应主动执行 `stop_robot.sh`。
4. 机器人附近应保留安全空间，避免突然运动造成碰撞。
5. 修改雷达方向、TF、地图、Nav2 参数前建议先备份当前可运行版本。
6. 比赛演示版本建议冻结配置，不再随意修改核心参数。

---

## 13. 项目成果

本项目已完成以下功能验证：

- 底盘运动控制正常。
- YDLIDAR X3 雷达 `/scan` 数据正常。
- 雷达前后、左右方向校正完成。
- 基于 slam-toolbox 构建 `patrol_map_v5` 地图。
- Nav2 可加载地图并完成目标点导航。
- 多点巡检脚本可按 A → B → C → D → E 顺序完成巡检。
- YOLO 可检测 `person` 类目标。
- 检测到人员后，系统可发布 `Person Detected` 状态。
- 最终巡检脚本可在异常时取消导航目标并主动停车。
- 状态恢复 `Normal` 后，机器人可继续执行巡检。
- Web 页面可显示实时画面和巡检状态。

---

## 14. 适用场景

本项目适合用于以下场景的原型验证：

- 实验室巡检
- 仓储通道巡查
- 设备间巡检
- 机房无人值守巡查
- 教学楼走廊巡检
- 小型办公区域安防巡查

---

## 15. 许可证

建议使用 Apache-2.0 License。请在仓库根目录放置 `LICENSE` 文件后再提交至 NodeHub。

---

## 16. 致谢

本项目基于 RDK X5、ROS2、TROS、Nav2、slam-toolbox、YDLIDAR ROS2 驱动和 WHEELTEC 底盘功能包完成开发与系统集成。
