#!/usr/bin/env python3
import math
import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import Twist


# =========================
# 在这里填写你从 RViz 取到的巡检点
# 格式：("点名", x, y)
# =========================
WAYPOINTS = [
    ("A", -2.9215, 4.9317),
    ("B", -4.0408, 4.2898),
    ("C", -4.5198, 4.9309),
    ("D", -4.8402, 5.4586),
    ("E", -3.6561, 6.0082),
]
LOOP_PATROL = False       # True：循环巡检；False：只跑一圈
PAUSE_SEC = 1.0          # 到达每个点后等待时间
CONTINUE_ON_FAIL = True  # 某个点失败后是否继续下一个点


def yaw_to_quaternion(yaw):
    """把 yaw 角转换成四元数，只用于 2D 导航"""
    qz = math.sin(yaw / 2.0)
    qw = math.cos(yaw / 2.0)
    return qz, qw


class PatrolNavNode(Node):
    def __init__(self):
        super().__init__('patrol_nav_node')

        self.nav_client = ActionClient(
            self,
            NavigateToPose,
            'navigate_to_pose'
        )

        self.stop_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.get_logger().info('多点巡检节点已启动')
        self.get_logger().info('等待 Nav2 navigate_to_pose action server...')

        self.nav_client.wait_for_server()

        self.get_logger().info('Nav2 已连接，可以开始多点巡检')

    def calc_yaw_to_next(self, index):
        """让小车到达当前点后，车头大致朝向下一个点"""
        name, x, y = WAYPOINTS[index]

        if index < len(WAYPOINTS) - 1:
            _, nx, ny = WAYPOINTS[index + 1]
        else:
            _, nx, ny = WAYPOINTS[0]

        return math.atan2(ny - y, nx - x)

    def send_stop(self):
        """主动发布 0 速度，防止底盘保持最后速度"""
        msg = Twist()
        for _ in range(20):
            self.stop_pub.publish(msg)
            time.sleep(0.05)

    def send_goal(self, name, x, y, yaw):
        goal_msg = NavigateToPose.Goal()

        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()

        goal_msg.pose.pose.position.x = float(x)
        goal_msg.pose.pose.position.y = float(y)
        goal_msg.pose.pose.position.z = 0.0

        qz, qw = yaw_to_quaternion(yaw)
        goal_msg.pose.pose.orientation.z = qz
        goal_msg.pose.pose.orientation.w = qw

        self.get_logger().info(
            f'发送目标点 {name}: x={x:.3f}, y={y:.3f}, yaw={yaw:.2f}'
        )

        send_future = self.nav_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, send_future)

        goal_handle = send_future.result()
        if not goal_handle.accepted:
            self.get_logger().error(f'目标点 {name} 被 Nav2 拒绝')
            self.send_stop()
            return False

        self.get_logger().info(f'目标点 {name} 已接受，开始导航...')

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        result = result_future.result()
        status = result.status

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f'已到达目标点 {name}')
            self.send_stop()
            time.sleep(PAUSE_SEC)
            return True
        else:
            self.get_logger().warn(f'目标点 {name} 导航失败，status={status}')
            self.send_stop()
            time.sleep(PAUSE_SEC)
            return False

    def run_patrol(self):
        round_count = 1

        while rclpy.ok():
            self.get_logger().info(f'开始第 {round_count} 轮巡检')

            for i, (name, x, y) in enumerate(WAYPOINTS):
                yaw = self.calc_yaw_to_next(i)
                success = self.send_goal(name, x, y, yaw)

                if not success and not CONTINUE_ON_FAIL:
                    self.get_logger().warn('巡检中止')
                    return

            self.get_logger().info(f'第 {round_count} 轮巡检完成')

            if not LOOP_PATROL:
                break

            round_count += 1


def main(args=None):
    rclpy.init(args=args)

    node = PatrolNavNode()

    try:
        node.run_patrol()
    except KeyboardInterrupt:
        node.get_logger().warn('收到 Ctrl+C，正在停车...')
        node.send_stop()
    finally:
        node.send_stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
