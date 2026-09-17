import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

class LocalizationNode(Node):
    def __init__(self):
        super().__init__('localization_node')

        self.callback_group = ReentrantCallbackGroup()

        self.camera_filtered_subscription = self.create_subscription(
            int,
            "/camera/data/filtered",
            self.handle_camera_filtered,
            10,
            callback_group=self.callback_group,
        )

        self.sensor_filtered_subscription = self.create_subscription(
            int,
            "/sensor/data/filtered",
            self.handle_sensor_filtered,
            10,
            callback_group=self.callback_group,
        )

        self.state_publisher = self.create_publisher(
            int, 
            "/localization/state", 
            10
        )

    def handle_camera_filtered(self, msg: int):
        return

    def handle_sensor_filtered(self, msg: int):
        return

def main(args=None):
    rclpy.init(args=args)
    node = LocalizationNode()
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