import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

"""
Convert direction vectors into motor commands
"""

class MotorCommandsNode(Node):
    def __init__(self):
        super().__init__('motor_commands_node')

        self.callback_group = ReentrantCallbackGroup()

        self.twist_subscription = self.create_subscription(
            int,
            "/twist",
            self.handle_twist,
            10,
            callback_group=self.callback_group,
        )

        self.motor_speeds_publisher = self.create_publisher(
            int, 
            "/motor/speeds", 
            10
        )

    def handle_twist(self, msg: int):
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