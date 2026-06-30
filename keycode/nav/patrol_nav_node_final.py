#!/usr/bin/env python3
import math
import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import Twist
from std_msgs.msg import String


# 你的多点巡检坐标
WAYPOINTS = [
    ("A", -2.9215, 4.9317),
    ("B", -4.0408, 4.2898),
    ("C", -4.5198, 4.9309),
    ("D", -4.8402, 5.4586),
    ("E", -3.6561, 6.0082),
]

LOOP_PATROL = False          # 第一次联动测试建议 False，只跑一圈
PAUSE_SEC = 1.0              # 到达每个点后等待时间
STOP_PUBLISH_TIMES = 20      # 每次停车发布 0 速度的次数
STOP_PUBLISH_PERIOD = 0.05   # 发布 0 速度间隔


def yaw_to_quaternion(yaw):
    qz = math.sin(yaw / 2.0)
    qw = math.cos(yaw / 2.0)
    return qz, qw


class PatrolNavNodeSafe(Node):
    def __init__(self):
        super().__init__('patrol_nav_node_safe')

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

        self.status_sub = self.create_subscription(
            String,
            '/patrol/status',
            self.status_callback,
            10
        )

        self.current_status = 'Unknown'
        self.abnormal_detected = False
        self.current_goal_handle = None
        self.cancel_requested = False

        self.get_logger().info('安全版多点巡检节点已启动')
        self.get_logger().info('等待 Nav2 navigate_to_pose action server...')

        self.nav_client.wait_for_server()

        self.get_logger().info('Nav2 已连接，可以开始安全多点巡检')
        self.get_logger().info('已订阅 /patrol/status，检测到人员异常会取消当前导航目标并停车')

    def status_callback(self, msg):
        status = msg.data.strip()
        self.current_status = status

        is_abnormal = (
            'Person' in status or
            'Detected' in status or
            'Abnormal' in status or
            '异常' in status or
            '人' in status
        ) and ('Normal' not in status)

        if is_abnormal and not self.abnormal_detected:
            self.get_logger().warn(f'收到异常状态：{status}，准备取消导航并停车')
            self.abnormal_detected = True
            self.cancel_current_goal()

        elif not is_abnormal and self.abnormal_detected:
            self.get_logger().info(f'异常状态解除：{status}，可以继续巡检')
            self.abnormal_detected = False
            self.cancel_requested = False

    def cancel_current_goal(self):
        if self.current_goal_handle is not None and not self.cancel_requested:
            try:
                self.get_logger().warn('正在取消当前 Nav2 目标...')
                self.current_goal_handle.cancel_goal_async()
                self.cancel_requested = True
            except Exception as e:
                self.get_logger().error(f'取消目标失败：{e}')

    def send_stop(self):
        msg = Twist()
        for _ in range(STOP_PUBLISH_TIMES):
            self.stop_pub.publish(msg)
            time.sleep(STOP_PUBLISH_PERIOD)

    def keep_stop_while_abnormal(self):
        self.get_logger().warn('进入异常停车保持状态，等待 /patrol/status 恢复 Normal...')

        while rclpy.ok() and self.abnormal_detected:
            self.send_stop()
            rclpy.spin_once(self, timeout_sec=0.1)

        self.send_stop()
        self.get_logger().info('异常解除，准备继续巡检')

    def calc_yaw_to_next(self, index):
        name, x, y = WAYPOINTS[index]

        if index < len(WAYPOINTS) - 1:
            _, nx, ny = WAYPOINTS[index + 1]
        else:
            _, nx, ny = WAYPOINTS[0]

        return math.atan2(ny - y, nx - x)

    def send_goal(self, name, x, y, yaw):
        if self.abnormal_detected:
            self.keep_stop_while_abnormal()

        goal_msg = NavigateToPose.Goal()

        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()

        goal_msg.pose.pose.position.x = float(x)
        goal_msg.pose.pose.position.y = float(y)
        goal_msg.pose.pose.position.z = 0.0

        qz, qw = yaw_to_quaternion(yaw)
        goal_msg.pose.pose.orientation.z = qz
        goal_msg.pose.pose.orientation.w = qw

        self.cancel_requested = False
        self.current_goal_handle = None

        self.get_logger().info(
            f'发送目标点 {name}: x={x:.3f}, y={y:.3f}, yaw={yaw:.2f}'
        )

        send_future = self.nav_client.send_goal_async(goal_msg)

        while rclpy.ok() and not send_future.done():
            rclpy.spin_once(self, timeout_sec=0.1)
            if self.abnormal_detected:
                self.send_stop()

        goal_handle = send_future.result()

        if goal_handle is None:
            self.get_logger().error(f'目标点 {name} 发送失败')
            self.send_stop()
            return 'failed'

        if not goal_handle.accepted:
            self.get_logger().error(f'目标点 {name} 被 Nav2 拒绝')
            self.send_stop()
            return 'failed'

        self.current_goal_handle = goal_handle

        self.get_logger().info(f'目标点 {name} 已接受，开始导航...')

        result_future = goal_handle.get_result_async()

        while rclpy.ok() and not result_future.done():
            rclpy.spin_once(self, timeout_sec=0.1)

            if self.abnormal_detected:
                self.get_logger().warn('巡检过程中检测到异常，持续发布 0 速度')
                self.cancel_current_goal()
                self.send_stop()

        self.send_stop()
        self.current_goal_handle = None

        result = result_future.result()
        status = result.status if result is not None else None

        if self.abnormal_detected:
            self.get_logger().warn(f'目标点 {name} 因异常事件中断，等待恢复后重试该点')
            self.keep_stop_while_abnormal()
            return 'retry'

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f'已到达目标点 {name}')
            time.sleep(PAUSE_SEC)
            return 'success'

        if status == GoalStatus.STATUS_CANCELED:
            self.get_logger().warn(f'目标点 {name} 被取消')
            return 'retry'

        self.get_logger().warn(f'目标点 {name} 导航失败，status={status}')
        return 'failed'

    def run_patrol(self):
        round_count = 1

        while rclpy.ok():
            self.get_logger().info(f'开始第 {round_count} 轮安全巡检')

            i = 0
            while i < len(WAYPOINTS) and rclpy.ok():
                name, x, y = WAYPOINTS[i]
                yaw = self.calc_yaw_to_next(i)

                result = self.send_goal(name, x, y, yaw)

                if result == 'success':
                    i += 1

                elif result == 'retry':
                    self.get_logger().info(f'准备重试目标点 {name}')
                    time.sleep(1.0)

                else:
                    self.get_logger().warn(f'目标点 {name} 失败，跳过该点')
                    i += 1

            self.get_logger().info(f'第 {round_count} 轮安全巡检完成')

            if not LOOP_PATROL:
                break

            round_count += 1

        self.send_stop()


def main(args=None):
    rclpy.init(args=args)

    node = PatrolNavNodeSafe()

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
