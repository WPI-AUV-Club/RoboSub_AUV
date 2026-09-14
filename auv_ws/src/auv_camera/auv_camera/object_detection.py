import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

"""
Turn processed camera data into object info
"""

class ObjectDetectionNode(Node):
    def __init__(self):
        super().__init__('object_detection_node')

        self.callback_group = ReentrantCallbackGroup()

        self.camera_filtered_subscription = self.create_subscription(
            int,
            "/camera/data/raw",
            self.handle_camera_filtered,
            10,
            callback_group=self.callback_group,
        )

        self.camera_detections_publisher = self.create_publisher(
            int, 
            "/camera/data/detections", 
            10
        )

    def handle_camera_filtered(self, msg: int):
        return

def main(args=None):
    rclpy.init(args=args)
    node = ObjectDetectionNode()
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