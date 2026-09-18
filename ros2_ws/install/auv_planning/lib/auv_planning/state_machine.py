import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from std_msgs.msg import Int32

class StateMachineNode(Node):
    def __init__(self):
        super().__init__('state_machine_node')

        self.callback_group = ReentrantCallbackGroup()

        self.camera_detections_subscription = self.create_subscription(
            Int32,
            "/camera/data/detections",
            self.handle_detections,
            10,
            callback_group=self.callback_group,
        )

        self.state_subscription = self.create_subscription(
            Int32,
            "/localization/state",
            self.handle_state,
            10,
            callback_group=self.callback_group,
        )

        self.emergency_subscription = self.create_subscription(
            Int32,
            "/emergency",
            self.handle_emergency,
            10,
            callback_group=self.callback_group,
        )

        self.goal_publisher = self.create_publisher(
            Int32, 
            "/goal", 
            10
        )

    def handle_detections(self, msg: Int32):
        return

    def handle_state(self, msg: Int32):
        return

    def handle_emergency(self, msg: Int32):
        return

def main(args=None):
    rclpy.init(args=args)
    node = StateMachineNode()
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