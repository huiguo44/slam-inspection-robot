#!/usr/bin/env python3
import os
import glob
import threading
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from flask import Flask, send_file, request
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist

app = Flask(__name__)

status_text = "Status: Waiting"
cmd_pub = None
latest_frame = None
bridge = CvBridge()

ROBOT_IP = "192.168.101.4"   # 改成你小车实际IP
IMAGE_DIR = "/home/wheeltec/patrol_images"


class WebRosNode(Node):
    def __init__(self):
        super().__init__("patrol_web_node")
        global cmd_pub
        cmd_pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.create_subscription(String, "/patrol/status", self.status_cb, 10)
        self.create_subscription(Image, "/web/image_raw", self.image_cb, 10)
    def status_cb(self, msg):
        global status_text
        status_text = msg.data
    def image_cb(self, msg):
        global latest_frame
        try:
            latest_frame = bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception:
            pass

def publish_cmd(x, z):
    msg = Twist()
    msg.linear.x = float(x)
    msg.angular.z = float(z)
    cmd_pub.publish(msg)

def gen_video():
    global latest_frame
    while True:
        if latest_frame is None:
            continue
        ok, jpeg = cv2.imencode(".jpg", latest_frame)
        if not ok:
            continue
        frame = jpeg.tobytes()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )


@app.route("/video")
def video():
    return app.response_class(
        gen_video(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )
@app.route("/")
def index():
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>智能巡检机器人控制台</title>
<style>
body {{ font-family: Arial; background:#111; color:white; text-align:center; }}
.card {{ background:#222; margin:12px; padding:15px; border-radius:12px; }}
button {{ font-size:22px; padding:12px 25px; margin:6px; border-radius:10px; }}
img {{ max-width:95%; border-radius:10px; }}
.status {{ font-size:22px; color:#00ff99; }}
</style>
<script>
function cmd(action) {{
  fetch('/cmd?action=' + action);
}}
function refreshStatus() {{
  fetch('/status').then(r=>r.text()).then(t=>document.getElementById('status').innerText=t);
  document.getElementById('alarm_img').src='/latest_image?t=' + Date.now();
}}
setInterval(refreshStatus, 1000);
</script>
</head>

<body>
<h1>SLAM智能巡检机器人</h1>

<div class="card">
<h2>实时巡检画面</h2>
<img src="/video">
</div>

<div class="card">
<h2>机器人状态</h2>
<div id="status" class="status">{status_text}</div>
</div>

<div class="card">
<h2>手动控制</h2>
<button onclick="cmd('forward')">前进</button><br>
<button onclick="cmd('left')">左转</button>
<button onclick="cmd('stop')">停止</button>
<button onclick="cmd('right')">右转</button><br>
<button onclick="cmd('back')">后退</button>
</div>

<div class="card">
<h2>最新报警截图</h2>
<img id="alarm_img" src="/latest_image">
</div>

</body>
</html>
"""


@app.route("/status")
def status():
    return status_text


@app.route("/cmd")
def cmd():
    action = request.args.get("action", "stop")

    if action == "forward":
        publish_cmd(0.15, 0.0)
    elif action == "back":
        publish_cmd(-0.15, 0.0)
    elif action == "left":
        publish_cmd(0.0, 0.5)
    elif action == "right":
        publish_cmd(0.0, -0.5)
    else:
        publish_cmd(0.0, 0.0)

    return "ok"


@app.route("/latest_image")
def latest_image():
    files = glob.glob(os.path.join(IMAGE_DIR, "*.jpg"))
    if not files:
        return "No image", 404
    latest = max(files, key=os.path.getmtime)
    return send_file(latest, mimetype="image/jpeg")


def ros_spin():
    rclpy.init()
    node = WebRosNode()
    rclpy.spin(node)


if __name__ == "__main__":
    threading.Thread(target=ros_spin, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
