#!/usr/bin/env python3
import os
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from ai_msgs.msg import PerceptionTargets
from geometry_msgs.msg import Twist

class YoloPatrolNode(Node):
    def __init__(self):
        super().__init__('yolo_patrol_node')

        self.conf_threshold = 0.60          # person 置信度阈值
        self.confirm_frames = 3            # 连续检测 3 帧才算一次异常
        self.lost_hold_frames = 5          # 连续丢失 5 帧后恢复正常
        self.abnormal_interval = 8.0       # 两次异常计数最少间隔 8 秒

        self.person_detect_frames = 0
        self.person_lost_frames = 0
        self.person_confirmed = False

        self.abnormal_count = 0
        self.last_abnormal_time = 0.0

        self.log_dir = '/home/wheeltec/patrol_logs'
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, 'yolo_abnormal_log.txt')

        self.sub = self.create_subscription(
            PerceptionTargets,
            '/hobot_dnn_detection',
            self.detection_callback,
            10
        )

        self.status_pub = self.create_publisher(
            String,
            '/patrol/status',
            10
        )
        
        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )
        self.get_logger().info('YOLO人体异常巡检节点已启动')
        self.get_logger().info('订阅: /hobot_dnn_detection')
        self.get_logger().info('发布: /patrol/status')
    def stop_robot(self):
        stop_msg = Twist()
        stop_msg.linear.x = 0.0
        stop_msg.linear.y = 0.0
        stop_msg.linear.z = 0.0
        stop_msg.angular.x = 0.0
        stop_msg.angular.y = 0.0
        stop_msg.angular.z = 0.0
        self.cmd_pub.publish(stop_msg)
    def detection_callback(self, msg):
        person_count = 0
        best_conf = 0.0

        for target in msg.targets:
            if target.type != 'person':
                continue

            for roi in target.rois:
                conf = float(roi.confidence)
                if conf >= self.conf_threshold:
                    person_count += 1
                    best_conf = max(best_conf, conf)

        raw_person_detected = person_count > 0

        if raw_person_detected:
            self.person_detect_frames += 1
            self.person_lost_frames = 0
        else:
            self.person_lost_frames += 1
            self.person_detect_frames = 0

        if self.person_detect_frames >= self.confirm_frames:
            self.person_confirmed = True

        if self.person_lost_frames >= self.lost_hold_frames:
            self.person_confirmed = False

        now = time.time()
        time_text = time.strftime('%Y-%m-%d %H:%M:%S')
        if self.person_confirmed:
            status_text = 'Status: Person Detected'
            self.stop_robot()
            if now - self.last_abnormal_time >= self.abnormal_interval:
                self.abnormal_count += 1
                self.last_abnormal_time = now

                log_line = (
                    f'{time_text}, '
                    f'event=person_detected, '
                    f'count={self.abnormal_count}, '
                    f'person_count={person_count}, '
                    f'best_conf={best_conf:.3f}\n'
                )

                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_line)

                self.get_logger().warn(
                    f'检测到人员异常！异常次数: {self.abnormal_count}, '
                    f'人数: {person_count}, 最高置信度: {best_conf:.2f}'
                )
        else:
            status_text = 'Status: Normal'

        status_msg = String()
        status_msg.data = (
            f'{status_text}, '
            f'abnormal_count={self.abnormal_count}, '
            f'person_count={person_count}, '
            f'best_conf={best_conf:.3f}'
        )
        self.status_pub.publish(status_msg)


def main():
    rclpy.init()
    node = YoloPatrolNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
