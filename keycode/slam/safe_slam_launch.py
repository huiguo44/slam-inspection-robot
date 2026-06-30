from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[
                get_package_share_directory("wheeltec_slam_toolbox")
                + '/config/mapper_params_online_async.yaml'
            ],
            remappings=[
                ('odom', 'odom_combined')
            ]
        )
    ])
