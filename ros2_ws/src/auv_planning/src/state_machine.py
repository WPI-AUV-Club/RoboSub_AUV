import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

class StateMachineNode(Node):
    def __init__(self):
        super().__init__('state_machine_node')

        self.callback_group = ReentrantCallbackGroup()

        self.camera_detections_subscription = self.create_subscription(
            int,
            "/camera/data/detections",
            self.handle_detections,
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

        self.emergency_subscription = self.create_subscription(
            int,
            "/emergency",
            self.handle_emergency,
            10,
            callback_group=self.callback_group,
        )

        self.goal_publisher = self.create_publisher(
            int, 
            "/goal", 
            10
        )

    def handle_detections(self, msg: int):
        return

    def handle_state(self, msg: int):
        return

    def handle_emergency(self, msg: int):
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