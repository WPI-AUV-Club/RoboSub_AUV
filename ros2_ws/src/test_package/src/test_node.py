#!/usr/bin/env python3

import rclpy
from rclpy.node import Node


class SimpleNode(Node):
    """
    Simple node to test within docker container.

    Prints hello from ros node
    """

    def __init__(self):
        """Init."""
        # Initialize the node with the name 'minimal_node'
        super().__init__("minimal_node")
        self.get_logger().info("Hello ROS 2 from Python!")


def main(args=None):
    """Main Loop."""
    # Initialize ROS 2 communications
    rclpy.init(args=args)

    # Create the node
    node = SimpleNode()

    # Keep the node alive to process callbacks
    rclpy.spin(node)

    # Shutdown cleanly
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
