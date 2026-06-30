本压缩包为《基于RDK X5的多模态SLAM智能巡检机器人》重点代码文件。

start：
包含最终演示启动脚本、底盘启动、雷达启动、Nav2启动和急停脚本。

nav：
包含基于 Nav2 的多点巡检程序。程序按 A→B→C→D→E 顺序发送导航目标，并订阅 /patrol/status。当检测到 Person Detected 状态时，程序取消当前导航目标，发布零速度停车，等待状态恢复后继续执行巡检。

yolo：
包含 YOLO 巡检状态节点。该节点订阅 /hobot_dnn_detection 目标检测结果，识别 person 类目标，并发布 /patrol/status 状态，同时记录异常事件。

web：
包含 Web 监控页面程序，用于显示实时画面、巡检状态、异常信息和控制按钮。

slam：
包含安全版 slam_toolbox 启动文件、Nav2 参数和地图加载配置。

lidar：
包含 YDLIDAR X3 雷达参数和机器人模型/雷达安装位姿配置。

map：
包含最终用于 Nav2 巡检的 patrol_map_v5 地图文件。
