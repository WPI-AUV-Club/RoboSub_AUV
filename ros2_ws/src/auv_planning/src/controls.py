import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

"""
Takes in path plan and do controls
"""

class ControlsNode(Node):
    def __init__(self):
        super().__init__('controls_node')

        self.callback_group = ReentrantCallbackGroup()

        self.path_subscription = self.create_subscription(
            int,
            "/path",
            self.handle_path,
            10,
            callback_group=self.callback_group,
        )

        self.state_subscription = self.create_subscription(
            int,
            "/localization/state",
            self.handle_state,
            10,
            callback_group=self.callback_group,
        )

        self.twist_publisher = self.create_publisher(
            int, 
            "/twist", 
            10
        )

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