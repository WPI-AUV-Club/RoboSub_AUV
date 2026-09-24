import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from std_msgs.msg import Int32

class SensorFilteringNode(Node):
    def __init__(self):
        super().__init__('sensor_filtering_node')

        self.callback_group = ReentrantCallbackGroup()

        self.sensor_raw_subscription = self.create_subscription(
            Int32,
            "/sensor/data/raw",
            self.handle_sensor_raw,
            10,
            callback_group=self.callback_group,
        )

        self.sensor_filtered_publisher = self.create_publisher(
            Int32, 
            "/sensor/data/filtered", 
            10
        )

    def handle_sensor_raw(self, msg: Int32):
        return

def main(args=None):
    rclpy.init(args=args)
    node = SensorFilteringNode()
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