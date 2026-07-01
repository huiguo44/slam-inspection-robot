# Multimodal SLAM Patrol Robot Based on RDK X5

## 1. Introduction

This project implements a multimodal SLAM patrol robot based on the RDK X5 robot development platform. It is designed for indoor semi-structured scenarios such as laboratories, warehouses, equipment rooms, corridors, and small office areas.

The system integrates a YDLIDAR X3 LiDAR, an IMX219-160IR infrared camera, ROS2, slam-toolbox, Nav2, YOLO object detection, and a Web monitoring interface. It supports 2D mapping, autonomous navigation, multi-point patrol, human detection, abnormal event handling, automatic stopping, status publishing, and browser-based monitoring.

Overall workflow:

```text
LiDAR / Camera
        ↓
ROS2 sensing and topic publishing
        ↓
slam-toolbox mapping + Nav2 localization and navigation
        ↓
Multi-point autonomous patrol
        ↓
YOLO human detection
        ↓
Emergency stop / Status publishing / Web monitoring
```

## 2. Features

- **SLAM Mapping**: Builds a 2D occupancy grid map using YDLIDAR X3 and slam-toolbox.
- **Autonomous Navigation**: Uses Nav2 for map loading, AMCL localization, path planning, and motion control.
- **Multi-point Patrol**: Sends navigation goals to predefined waypoints such as A, B, C, D, and E.
- **YOLO Human Detection**: Detects the `person` class in camera images using RDK X5 edge inference.
- **Abnormal Event Handling**: Cancels the current navigation goal and publishes zero velocity when a person is detected during patrol.
- **Resume Patrol**: Continues the unfinished patrol task after the abnormal status returns to Normal.
- **Web Monitoring**: Provides a browser-based interface for real-time video, detection status, patrol status, and alarm information.
- **Modular Code Structure**: Key code is organized by LiDAR, map, navigation, SLAM, startup scripts, Web, and YOLO modules.

## 3. Hardware Platform

| Module | Model / Name | Function |
|---|---|---|
| Main controller | RDK X5 | Runs ROS2, TROS, YOLO, Nav2, and Web services |
| Mobile base | R550A_PLUS_diff_arm | Mobile robot motion platform |
| Base controller | STM32 controller | Receives `/cmd_vel` and drives motors |
| LiDAR | YDLIDAR X3 | Publishes `/scan` for SLAM, localization, and obstacle avoidance |
| Camera | IMX219-160IR infrared camera | Captures patrol images for YOLO detection and Web display |
| Display / Debugging | HDMI screen / PC / mobile browser | RViz debugging and Web monitoring |

## 4. Software Environment

| Software / Framework | Description |
|---|---|
| Ubuntu 22.04 | RDK X5 system environment |
| ROS2 Humble | Robot communication, mapping, and navigation framework |
| TROS | RDK X5 vision algorithm and inference environment |
| slam-toolbox | 2D SLAM mapping |
| Nav2 | AMCL localization, path planning, and motion control |
| YDLIDAR ROS2 Driver | Driver for YDLIDAR X3 |
| dnn_node_example / hobot_dnn | YOLO object detection inference |
| OpenCV / cv_bridge | Image processing and ROS image conversion |
| Flask | Web monitoring service |

## 5. Repository Structure

All key code files are stored under the `keycode` directory.

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

## 6. Main Files

### 6.1 `keycode/lidar`

| File | Description |
|---|---|
| `X3.yaml` | Configuration file for YDLIDAR X3, including serial port, baud rate, and scan direction |
| `robot_model.yaml` | Robot model and sensor transform configuration |

### 6.2 `keycode/map`

| File | Description |
|---|---|
| `patrol_map_v5.pgm` | Final 2D grid map used by Nav2 |
| `patrol_map_v5.yaml` | Map metadata such as resolution, origin, and thresholds |

### 6.3 `keycode/nav`

| File | Description |
|---|---|
| `patrol_nav_node.py` | Basic multi-point patrol script |
| `patrol_nav_node_safe.py` | Safer patrol script with abnormal status subscription and stopping logic |
| `patrol_nav_node_final.py` | Final demo patrol script for multi-point patrol and abnormal stop integration |

### 6.4 `keycode/slam`

| File | Description |
|---|---|
| `safe_slam_launch.py` | Safe SLAM launch file that only starts slam-toolbox to avoid launching duplicated base or LiDAR nodes |
| `WHEELTEC.yaml` | Nav2 map loading configuration |
| `param_R550A_PLUS_diff_arm.yaml` | Nav2 parameter file for the R550A_PLUS_diff_arm base |

### 6.5 `keycode/start`

| File | Description |
|---|---|
| `start_base.sh` | Starts the mobile base communication node |
| `start_lidar.sh` | Starts the YDLIDAR X3 node |
| `start_nav.sh` | Starts the Nav2 navigation system |
| `start_demo_prepare.sh` | Starts base, LiDAR, Nav2, YOLO, and Web modules for final demonstration |
| `start_patrol_final.sh` | Starts the final patrol script after RViz initial pose setup |
| `stop_robot.sh` | Emergency stop script that continuously publishes zero velocity to `/cmd_vel` |

### 6.6 `keycode/web`

| File | Description |
|---|---|
| `compressed_to_raw.py` | Image conversion node used by the Web display pipeline |
| `patrol_web.py` | Flask Web monitoring service |

### 6.7 `keycode/yolo`

| File | Description |
|---|---|
| `yolo_patrol_node.py` | Subscribes to YOLO detection results, detects the `person` class, and publishes `/patrol/status` |

## 7. Deployment

This repository stores the key code and configuration files. During deployment, copy the corresponding files to the RDK X5 robot environment. Please back up original configuration files before replacing them.

### 7.1 Grant Execution Permission

```bash
chmod +x keycode/start/*.sh
chmod +x keycode/nav/*.py
chmod +x keycode/web/*.py
chmod +x keycode/yolo/*.py
chmod +x keycode/slam/*.py
```

### 7.2 Recommended Deployment

If the scripts use absolute paths under `/home/wheeltec/`, copy the key scripts to `/home/wheeltec/`:

```bash
cp keycode/start/*.sh /home/wheeltec/
cp keycode/nav/*.py /home/wheeltec/
cp keycode/web/*.py /home/wheeltec/
cp keycode/yolo/*.py /home/wheeltec/
cp keycode/slam/safe_slam_launch.py /home/wheeltec/
```

Copy the map files to:

```bash
mkdir -p /home/wheeltec/maps
cp keycode/map/patrol_map_v5.* /home/wheeltec/maps/
```

For configuration files such as `WHEELTEC.yaml`, `param_R550A_PLUS_diff_arm.yaml`, `X3.yaml`, and `robot_model.yaml`, back up the original files first and then replace them according to the actual project paths.

## 8. Startup Guide

### 8.1 Final Demo Startup

The final demo is divided into two steps: start the basic modules first, set the initial pose in RViz, and then start the patrol script.

#### Step 1: Start Demo Preparation Script

```bash
cd /home/wheeltec
chmod +x start_demo_prepare.sh
./start_demo_prepare.sh
```

This script starts the mobile base, LiDAR, Nav2, YOLO detection, and Web service, but does not start the patrol task immediately.

#### Step 2: Set Initial Pose in RViz

Open RViz and configure:

```text
Fixed Frame = map
Map Topic = /map
LaserScan Topic = /scan
```

Use `2D Pose Estimate` to align the robot pose with the map. Confirm that the `/scan` point cloud overlaps with the map walls.

#### Step 3: Start Final Patrol

```bash
cd /home/wheeltec
chmod +x start_patrol_final.sh
./start_patrol_final.sh
```

The robot will start autonomous patrol along the predefined waypoints. If YOLO detects a person during patrol, the robot cancels the current Nav2 goal and stops. After the status returns to Normal, the robot continues the remaining patrol task.

### 8.2 Single-module Startup

```bash
# Start mobile base
./start_base.sh

# Start LiDAR
./start_lidar.sh

# Start Nav2
./start_nav.sh

# Emergency stop
./stop_robot.sh
```

### 8.3 Web Monitoring

Open the following URL in a browser:

```text
http://<RDK_X5_IP>:5000
```

Replace `<RDK_X5_IP>` with the actual IP address of the RDK X5.

The Web page displays:

- Real-time patrol image
- YOLO detection status
- `/patrol/status`
- Alarm information
- Manual control buttons

## 9. Key ROS2 Topics

| Topic | Function |
|---|---|
| `/cmd_vel` | Mobile base velocity control |
| `/odom` | Odometry feedback |
| `/imu` | IMU data |
| `/tf`, `/tf_static` | Coordinate transforms |
| `/scan` | LiDAR scan data |
| `/map` | Map used by SLAM and Nav2 |
| `/image_raw` | Raw camera image |
| `/hobot_dnn_detection` | YOLO detection results |
| `/patrol/status` | Patrol and abnormal status |
| `/web/image_raw` | Image stream used by Web display |

## 10. Test Results

The following functions have been verified:

- The mobile base responds to `/cmd_vel` velocity commands.
- YDLIDAR X3 publishes valid `/scan` data.
- slam-toolbox builds an indoor 2D map.
- Nav2 loads the map and completes goal navigation.
- The patrol script completes autonomous A → B → C → D → E multi-point patrol.
- YOLO detects the `person` class.
- The robot cancels navigation and stops when a person is detected during patrol.
- The robot resumes the unfinished patrol task after the abnormal status disappears.
- The Web page displays real-time video, patrol status, and alarm information.

## 11. Notes

1. Before starting the final patrol, set the initial pose in RViz using `2D Pose Estimate`.
2. If the `/scan` point cloud does not overlap with the map, check the initial pose, LiDAR direction, and TF configuration.
3. Do not stop `/cmd_vel` tests only by pressing `Ctrl + C`. Publish zero velocity or run `stop_robot.sh`.
4. Back up original Nav2, LiDAR, and robot model configuration files before replacing them.
5. For live demonstration, use a stable network. The Web interface can be accessed from a PC or mobile browser.

## 12. License

This project is released under the Apache License 2.0. See the `LICENSE` file for details.
