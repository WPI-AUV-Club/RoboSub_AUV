import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

class PathPlanningNode(Node):
    def __init__(self):
        super().__init__('path_planning_node')

        self.callback_group = ReentrantCallbackGroup()

        self.state_subscription = self.create_subscription(
            int,
            "/localization/state",
            self.handle_state,
            10,
            callback_group=self.callback_group,
        )

        self.goal_subscription = self.create_subscription(
            int,
            "/goal",
            self.handle_goal,
            10,
            callback_group=self.callback_group,
        )

        self.path_publisher = self.create_publisher(
            int, 
            "/path", 
            10
        )

    def handle_state(self, msg: int):
        return

    def handle_goal(self, msg: int):
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