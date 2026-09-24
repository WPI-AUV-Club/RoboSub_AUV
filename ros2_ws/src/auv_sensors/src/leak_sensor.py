import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from std_msgs.msg import Int32

class LeakSensorNode(Node):
    def __init__(self):
        super().__init__('leak_sensor_node')

        self.emergency_publisher = self.create_publisher(
            Int32, 
            "/goal", 
            10
        )

def main(args=None):
    rclpy.init(args=args)
    node = LeakSensorNode()
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