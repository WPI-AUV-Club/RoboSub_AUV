import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

"""
Send out motor commands
"""

class UARTManagerNode(Node):
    def __init__(self):
        super().__init__('uart_manager_node')

        self.callback_group = ReentrantCallbackGroup()

        self.motor_speed_subscription = self.create_subscription(
            int,
            "/motor/speeds",
            self.handle_speeds,
            10,
            callback_group=self.callback_group,
        )

    def handle_speeds(self, msg: int):
        return

def main(args=None):
    rclpy.init(args=args)
    node = UARTManagerNode()
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