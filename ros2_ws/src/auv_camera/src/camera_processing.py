import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from std_msgs.msg import Int32

"""
Process the raw camera data and send it to object detection
"""

class CameraProcessingNode(Node):
    def __init__(self):
        super().__init__('camera_processing_node')

        self.callback_group = ReentrantCallbackGroup()

        self.camera_raw_subscription = self.create_subscription(
            Int32,
            "/camera/data/raw",
            self.handle_camera_raw,
            10,
            callback_group=self.callback_group,
        )

        self.camera_filtered_publisher = self.create_publisher(
            Int32, 
            "/camera/data/filtered", 
            10
        )

    def handle_camera_raw(self, msg: Int32):
        return

def main(args=None):
    rclpy.init(args=args)
    node = CameraProcessingNode()
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