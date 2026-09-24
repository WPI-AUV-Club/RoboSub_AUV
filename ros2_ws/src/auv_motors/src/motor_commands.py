#!/usr/bin/env python3

import rclpy
from auv_motors.msg import MotorCommands
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from geometry_msgs.msg import Twist

"""
Convert direction vectors into motor commands
"""

class MotorCommandsNode(Node):
    def __init__(self):
        super().__init__('motor_commands_node')

        self.callback_group = ReentrantCallbackGroup()

        self.twist_subscription = self.create_subscription(
            Twist,
            "/twist",
            self.handle_twist,
            10,
            callback_group=self.callback_group,
        )

        self.motor_speeds_publisher = self.create_publisher(
            MotorCommands, 
            "/motor/speeds", 
            10
        )

    def handle_twist(self, msg: Twist):
        return

    

def main(args=None):
    rclpy.init(args=args)
    node = MotorCommandsNode()
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