#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage, Image
from cv_bridge import CvBridge
import cv2
import numpy as np


class CompressedToRaw(Node):
    def __init__(self):
        super().__init__('compressed_to_raw')
        self.bridge = CvBridge()

        self.sub = self.create_subscription(
            CompressedImage,
            '/image',
            self.cb,
            10
        )

        self.pub = self.create_publisher(
            Image,
            '/web/image_raw',
            10
        )

        self.get_logger().info('订阅 /image(CompressedImage)，发布 /web/image_raw(Image)')

    def cb(self, msg):
        np_arr = np.frombuffer(msg.data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return

        out_msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        out_msg.header = msg.header
        self.pub.publish(out_msg)


def main():
    rclpy.init()
    node = CompressedToRaw()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
