#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import Joy

"""
Takes in path plan and do controls
"""

class ControlsNode(Node):
    def __init__(self):
        super().__init__('controls_node')

        self.callback_group = ReentrantCallbackGroup()

        self.joystick_subscription = self.create_subscription(
            Joy,
            "/joy",
            self.handle_joy,
            10,
            callback_group=self.callback_group,
        )

        self.twist_publisher = self.create_publisher(
            TwistStamped, 
            "/twist", 
            10
        )

    def handle_joy(self, msg: Joy):
        header = msg.header   # timestamp in the header is the time the data is received from the joystick
        axes = msg.axes       # float32[] the axes measurements from a joystick
        buttons = msg.buttons # int32[] the buttons measurements from a joystick 

        commanded_twist = TwistStamped()
        commanded_twist.twist.linear.x = axes[1]
        commanded_twist.twist.angular.z = axes[0]

        self.publish_twist(commanded_twist)
        return

    def publish_twist(self, msg: TwistStamped):
        self.twist_publisher.publish(msg)
        return

def main(args=None):
    rclpy.init(args=args)
    node = ControlsNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()