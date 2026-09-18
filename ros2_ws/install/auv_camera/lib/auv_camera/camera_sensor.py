import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from std_msgs.msg import Int32

"""
Camera
"""

class CameraSensorNode(Node):
    def __init__(self):
        super().__init__('camera_sensor_node')

        self.camera_raw_publisher = self.create_publisher(
            Int32, 
            "/camera/data/raw", 
            10
        )


def main(args=None):
    rclpy.init(args=args)
    node = CameraSensorNode()
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