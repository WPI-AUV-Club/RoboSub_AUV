import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

class SensorNode(Node):
    def __init__(self):
        super().__init__('sensor_node')

        self.sensor_raw_publisher = self.create_publisher(
            int, 
            "/sensor/data/raw", 
            10
        )

def main(args=None):
    rclpy.init(args=args)
    node = SensorNode()
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