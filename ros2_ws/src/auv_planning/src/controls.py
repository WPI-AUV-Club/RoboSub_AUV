#!/usr/bin/env python3
import rclpy
from geometry_msgs.msg import Twist
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import Int32

"""
Takes in path plan and do controls
"""


class ControlsNode(Node):
    def __init__(self):
        super().__init__("controls_node")

        self.callback_group = ReentrantCallbackGroup()

        self.path_subscription = self.create_subscription(
            Int32,
            "/path",
            self.handle_path,
            10,
            callback_group=self.callback_group,
        )

        self.state_subscription = self.create_subscription(
            Int32,
            "/localization/state",
            self.handle_state,
            10,
            callback_group=self.callback_group,
        )

        self.twist_publisher = self.create_publisher(Twist, "/twist", 10)

        self.timer = self.create_timer(1.0, self.publish_twist)

    def publish_twist(self):
        msg = Twist()
        msg.linear.x = 1.0  # placeholder value for testing
        self.twist_publisher.publish(msg)
        self.get_logger().info("Published twist")

    def handle_path(self, msg: int):
        return

    def handle_state(self, msg: int):
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
