import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from std_msgs.msg import Int32

class PathPlanningNode(Node):
    def __init__(self):
        super().__init__('path_planning_node')

        self.callback_group = ReentrantCallbackGroup()

        self.state_subscription = self.create_subscription(
            Int32,
            "/localization/state",
            self.handle_state,
            10,
            callback_group=self.callback_group,
        )

        self.goal_subscription = self.create_subscription(
            Int32,
            "/goal",
            self.handle_goal,
            10,
            callback_group=self.callback_group,
        )

        self.path_publisher = self.create_publisher(
            Int32, 
            "/path", 
            10
        )

    def handle_state(self, msg: Int32):
        return

    def handle_goal(self, msg: Int32):
        return

def main(args=None):
    rclpy.init(args=args)
    node = PathPlanningNode()
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