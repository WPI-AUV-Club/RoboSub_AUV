#!/usr/bin/env python3

import math

import numpy as np
import rclpy
import tf2_geometry_msgs  # noqa

# from control.action import FollowPath
from geometry_msgs.msg import PointStamped, PoseStamped, TwistStamped
from nav_msgs.msg import GridCells, MapMetaData, OccupancyGrid, Path  # noqa: F401
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import Int32
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener

"""
Takes in path plan and do controls
"""


# CONSTANTS
PID_TOLERANCE = 0.05

TURN_FOV = 0.4

KP_LINEAR = 2.0
KP_ANGULAR = 3.6

FREQUENCY = 20

MAX_ANGULAR_SPEED = 2.4
MAX_LINEAR_SPEED = 1.0

DRIVE_TOLERANCE = 0.01
ROTATE_TOLERANCE = 0.08

# Pure pursuit circle radius (m). Larger lookahead lets the robot carry more
# speed on frontier paths instead of chasing points 10 cm ahead.
LOOK_AHEAD_DIST = 0.08


# FIGURE OUT TF TRANSFORM MATH
class ControlsNode(Node):
    def __init__(self):
        super().__init__("controls_node")

        self.callback_group = ReentrantCallbackGroup()
        
        # CHECK WHY LIST[INT32] DID NOT WORK, INT32 IS TEMPORARY
        self.path_subscription = self.create_subscription(
            Int32,
            "/path",
            self.handle_path,
            10,
            callback_group=self.callback_group,
        )

        self.state_subscription = self.create_subscription(
            Int32,
            "/localization/state",
            self.handle_robot_state,
            10,
            callback_group=self.callback_group,
        )

        self.twist_publisher = self.create_publisher(TwistStamped, "/twist", 10)

        self.timer = self.create_timer(1.0, self.publish_twist)

        # this publishes velocity cmds to make the robot move
        self.cmd_vel_publisher = self.create_publisher(TwistStamped, "/cmd_vel", 10)

        self.goal_point_publisher = self.create_publisher(
            PointStamped, "/pure_pursuit/goal_point", 10
        )

        # tf stuff so we can convert between map and odom frames
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self)

        # robots current position, gets updated by odom callback
        self.px = 0.0
        self.py = 0.0
        self.pz = 0.0
        self.pth = 0.0
        self.psi = 0.0

        self.pursuing = False
        self.points = []
        self.LFindex = 0
        self.final_point = None
        self.control_timer = self.create_timer(0.05, self.control_loop)

    def publish_twist(self):
        msg = TwistStamped()
        msg.twist.linear.x = 1.0  # placeholder value for testing
        self.twist_publisher.publish(msg)
        self.get_logger().info("Published twist")

    # EDIT TO WORK IN 3D SPACE
    def send_speed(self, linear_speed, angular_speed):
        """
        Sends twist to the /cmd_vel topic, which runs the AUV motors.
        :param linear_speed  [float, float, float] [m/s]   The linear speed in x y z.
        :param angular_speed [float, float, float] [rad/s] The angular speed for rotating around the body center, roll, pitch, yaw.
        """
        msg = TwistStamped()

        # self.get_logger().info(f"angular: {angular_speed}")

        # if infinity, set to 0
        if not np.isfinite(linear_speed):
            linear_speed = [0.0, 0.0, 0.0]
        if not np.isfinite(angular_speed):
            angular_speed = [0.0, 0.0, 0.0]

        # if total linear speed (magnitude of speed vector) is greater than MAX SPEED then clamp it down while preserving geometric orientation.
        linear_speed = np.asarray(linear_speed, float)
        mag = np.linalg.norm(linear_speed)
        if mag > MAX_LINEAR_SPEED:
            linear_speed *= MAX_LINEAR_SPEED / mag

        angular_speed = np.clip(
            angular_speed, -MAX_ANGULAR_SPEED, MAX_ANGULAR_SPEED
        ).tolist()

        # self.get_logger().info(f"linear speed: {linear_speed}")
        # self.get_logger().info(f"angular speed: {angular_speed}")

        msg.twist.linear.x = linear_speed[0]
        msg.twist.linear.y = linear_speed[1]
        msg.twist.linear.z = linear_speed[2]
        msg.twist.angular.z = angular_speed[2]
        msg.twist.angular.z = angular_speed[0]
        msg.twist.angular.z = angular_speed[0]
        self.cmd_vel_publisher.publish(msg)

    def handle_path(self, msg: Path):
        self.get_logger().info("handling pursuit path")
        if not path.poses:
            self.get_logger().warn("received empty path for pure pursuit")
            self.pursuing = False
            self.send_speed(0.0, 0.0)
            return

        # transform each waypoint into map frame so everything lines up
        transformed_poses = []
        for p in path.poses:
            try:
                p_map = self._tf_buffer.transform(p, "map")
                transformed_poses.append(p_map)
            except Exception as e:
                self.get_logger().warn(f"couldnt do tf transform: {e}")
                return

        collapsed = self._collapse_duplicate_waypoints(transformed_poses, 1e-3)
        new_points = [
            (p.pose.position.x, p.pose.position.y, p.pose.position.z) for p in collapsed
        ]
        if len(new_points) < 2:
            self.get_logger().warn("path collapsed to a single point; check planner")

        # set all the state before flipping pursuing=True so the control loop
        # doesnt see new pursuing flag with old points
        self.points = new_points
        self.final_point = new_points[-1]
        self.LFindex = 0
        self.pursuing = True
        return

    # EDIT TO MATCH NEW ROBOT STATE MESSAGE TYPE
    def handle_robot_state(self, msg: int):
        """
        A callback that updates the current pose of the robot
        :param msg [Odometry] the current odometry information
        """
        # self.get_logger().info("updating odom...")
        # wrap odom pose into a PoseStamped so we can transform it
        pose_odom = PoseStamped()
        pose_odom.header = msg.header
        pose_odom.header.frame_id = "odom"
        pose_odom.pose = msg.pose.pose

        # convert from odom frame to map frame so everything is consistent
        try:
            pose_map = cast(
                PoseStamped,
                self._tf_buffer.transform(pose_odom, "map"),
            )
        except Exception:
            return

        # update position
        self.px = pose_map.pose.position.x
        self.py = pose_map.pose.position.y
        self.pz = pose_map.pose.position.z

        # UPDATE TO RECORD PITCH AND ROLL, AND HANDLE THAT IN PURE PURSUIT ALGORITIHM
        # quaternion to euler bc we only need yaw
        quat = pose_map.pose.orientation
        (roll, pitch, yaw) = Rotation.from_quat(
            [quat.x, quat.y, quat.z, quat.w]
        ).as_euler("xyz")
        self.pth = yaw

        return

    def plos(self, path, LFindex, k1_psi=1.0, k2_psi=0.05, k1_theta=1.0, k2_theta=0.05):
        """
        Path following algorithm.
        path    : list of (x, y, z) waypoints, z down (NED)
        LFindex : index i of the current segment (path[i] -> path[i+1])
        Returns : (r_d, q_d, LFindex)  yaw-rate and pitch-rate commands, updated index
        Assumes self.psi (yaw) and self.theta (pitch) hold the robot's attitude;
        rename them to whatever your state uses.
        """
        if not path or len(path) < 2:
            return 0.0, 0.0, 0

        p = np.array([self.px, self.py, self.pz], dtype=float)
        i = max(0, min(LFindex, len(path) - 2))

        while True:
            Wi = np.array(path[i], dtype=float)
            Wj = np.array(path[i + 1], dtype=float)
            dW = Wj - Wi
            seg_len = np.linalg.norm(dW)

            # skip duplicate waypoints (zero-length segment)
            if seg_len < 1e-9:
                if i < len(path) - 2:
                    i += 1
                    continue
                return 0.0, 0.0, i

            alpha = math.atan2(dW[1], dW[0])
            beta = math.atan2(-dW[2], math.hypot(dW[0], dW[1]))  # z down: climb > 0

            cosa, sina = math.cos(alpha), math.sin(alpha)
            cosb, sinb = math.cos(beta), math.sin(beta)
            Rz = np.array([[cosa, sina, 0.0], [-sina, cosa, 0.0], [0.0, 0.0, 1.0]])
            Ry = np.array([[cosb, 0.0, -sinb], [0.0, 1.0, 0.0], [sinb, 0.0, cosb]])

            # path-frame error: ex along-track, ey cross-track, ez vertical-track
            ex, ey, ez = Ry @ Rz @ (p - Wi)

            # passed the end of this segment? move on to the next one
            if ex >= seg_len and i < len(path) - 2:
                i += 1
                self.get_logger().debug(f"plos segment index: {i}")
                continue
            break

        # pure pursuit terms: aim at the next waypoint
        psi_d = math.atan2(Wj[1] - p[1], Wj[0] - p[0])
        Wj_R, p_R = Rz @ Wj, Rz @ p
        theta_d = math.atan2(p_R[2] - Wj_R[2], Wj_R[0] - p_R[0])

        dpsi = (psi_d - self.psi + math.pi) % (
            2.0 * math.pi
        ) - math.pi  # wrap to [-pi, pi]

        # PLOS: pursuit term + line-of-sight (cross-track) term
        r_d = k1_psi * dpsi + k2_psi * (-ey)
        q_d = k1_theta * (theta_d - self.pth) + k2_theta * ez

        return r_d, q_d, i

    #  def pure_pursuit(self, path, LFindex):
    #     if not path:
    #         return [self.px, self.py, self.pz], 0

    #     last_found_index = max(0, min(LFindex, len(path) - 1))
    #     goal_pt = [path[last_found_index][0], path[last_found_index][1]]

    #     for i in range(last_found_index, len(path) - 1):
    #         x1, y1, z1 = path[i]
    #         x2, y2, z2 = path[i + 1]

    #         x1_offset = x1 - self.px
    #         y1_offset = y1 - self.py
    #         z1_offset = z1 - self.pz
    #         x2_offset = x2 - self.px
    #         y2_offset = y2 - self.py
    #         z2_offset = z2 - self.pz

    #         dx = x2_offset - x1_offset
    #         dy = y2_offset - y1_offset
    #         dz = z2_offset - z1_offset
    #         dr2 = dx**2 + dy**2

    #         if dr2 == 0:
    #             continue

    #         D = x1_offset * y2_offset - x2_offset * y1_offset
    #         discriminant = LOOK_AHEAD_DIST**2 * dr2 - D**2
    #         if discriminant < 0:
    #             continue

    #         sqrt_disc = math.sqrt(discriminant)

    #         x_sol1 = (D * dy + sgn(dy) * dx * sqrt_disc) / dr2
    #         y_sol1 = (-D * dx + abs(dy) * sqrt_disc) / dr2
    #         x_sol2 = (D * dy - sgn(dy) * dx * sqrt_disc) / dr2
    #         y_sol2 = (-D * dx - abs(dy) * sqrt_disc) / dr2

    #         pt1 = [x_sol1 + self.px, y_sol1 + self.py]
    #         pt2 = [x_sol2 + self.px, y_sol2 + self.py]

    #         minX, maxX = min(x1, x2), max(x1, x2)
    #         minY, maxY = min(y1, y2), max(y1, y2)
    #         eps = 1e-6
    #         candidates = []
    #         if (
    #             minX - eps <= pt1[0] <= maxX + eps
    #             and minY - eps <= pt1[1] <= maxY + eps
    #         ):
    #             candidates.append(pt1)
    #         if (
    #             minX - eps <= pt2[0] <= maxX + eps
    #             and minY - eps <= pt2[1] <= maxY + eps
    #         ):
    #             candidates.append(pt2)
    #         if not candidates:
    #             continue

    #         # Prefer the candidate farther along the current segment (toward segment end).
    #         if len(candidates) == 2:
    #             d1 = distance_between_pts(candidates[0], [x2, y2])
    #             d2 = distance_between_pts(candidates[1], [x2, y2])
    #             candidate = candidates[0] if d1 < d2 else candidates[1]
    #         else:
    #             candidate = candidates[0]

    #         # Only accept intersections that are ahead along the segment.
    #         if distance_between_pts(candidate, [x2, y2]) < distance_between_pts(
    #             [self.px, self.py], [x2, y2]
    #         ):
    #             goal_pt = candidate
    #             last_found_index = i
    #             self.get_logger().debug(f"lf index 1: {last_found_index}")
    #             break
    #         else:
    #             last_found_index = i + 1
    #             self.get_logger().debug(f"lf index 2: {last_found_index}")

    #     if any(math.isnan(coord) for coord in goal_pt):
    #         goal_pt = [self.px, self.py]

    #     return goal_pt, last_found_index

    @staticmethod
    def _collapse_duplicate_waypoints(
        poses: list[PoseStamped], min_step_m: float
    ) -> list[PoseStamped]:
        """
        3DOF (and dense grid) paths can repeat the same (x, y) while the pose
        rotates in place. Pure pursuit treats consecutive identical points as
        zero-length segments (skipped), which breaks lookahead at sharp turns.
        Keep one pose per distinct position so each segment has nonzero length.
        """
        if not poses:
            return []
        out: list[PoseStamped] = [poses[0]]
        for pose in poses[1:]:
            px, py = out[-1].pose.position.x, out[-1].pose.position.y
            qx, qy = pose.pose.position.x, pose.pose.position.y
            if math.hypot(qx - px, qy - py) >= min_step_m:
                out.append(pose)
        if len(out) == 1 and len(poses) > 1:
            out.append(poses[-1])
        return out

    def control_loop(self):
        if not self.pursuing:
            return

        dist_to_end = distance_between_pts([self.px, self.py], self.final_point)

        if dist_to_end < DRIVE_TOLERANCE:
            self.send_speed(0.0, 0.0)
            self.get_logger().info("goal reached 1")
            self.pursuing = False
            return

        goalPt, self.LFindex = self.pure_pursuit(self.points, self.LFindex)

        # Error calculations
        dx = goalPt[0] - self.px
        dy = goalPt[1] - self.py

        dist = math.sqrt(dx**2 + dy**2)
        # when the lookahead is basically sitting on the last waypoint, use
        # the actual remaining distance so we slow down smoothly at the end
        if distance_between_pts(goalPt, self.final_point) < DRIVE_TOLERANCE:
            dist = dist_to_end

        linear_speed = min(KP_LINEAR * dist, MAX_LINEAR_SPEED)

        angle = math.atan2(dy, dx)
        angular_error = correct_angle(angle - self.pth)

        if abs(angular_error) > ROTATE_TOLERANCE:
            angular_speed = angular_error * KP_ANGULAR
        else:
            angular_speed = 0.0

        # Do not drive forward hard while pointed away from the lookahead.
        # Otherwise the robot "cuts" 90° corners and slides toward obstacles.
        heading_alignment = math.cos(angular_error)
        heading_alignment = max(heading_alignment, 0.0)
        linear_speed *= heading_alignment

        # publish where pure pursuit is aiming so we can see it in rviz
        lookahead_marker = PointStamped()
        lookahead_marker.header.stamp = self.get_clock().now().to_msg()
        lookahead_marker.header.frame_id = "map"
        lookahead_marker.point.x = goalPt[0]
        lookahead_marker.point.y = goalPt[1]
        self.goal_point_publisher.publish(lookahead_marker)

        if dist >= DRIVE_TOLERANCE:
            if abs(angular_error) > TURN_FOV:
                linear_speed = 0.0

            self.send_speed(linear_speed, angular_speed)
        else:
            self.send_speed(0.0, 0.0)
            self.pursuing = False


def main(args=None):
    rclpy.init(args=args)
    node = ControlsNode()
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


def correct_angle(angle):
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle


def sgn(num):
    if num < 0:
        return -1
    else:
        return 1


def distance_between_pts(pt1, pt2):
    dx = pt2[0] - pt1[0]
    dy = pt2[1] - pt1[1]
    dz = pt2[2] - pt1[3]
    return math.sqrt(dx**2 + dy**2 + dz**2)
