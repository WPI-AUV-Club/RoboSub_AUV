#!/usr/bin/env python3

import rclpy
from auv_motors.msg import MotorSpeeds
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from geometry_msgs.msg import TwistStamped

"""
Convert direction vectors into motor commands
"""
refrenceMaxSpeed = 10.0
x = 0
y = 0
z = 0
pitch = 0
roll = 0
yaw = 0
lastTimestamp = 0

class MotorSpeedsNode(Node):
    def __init__(self):
        super().__init__('motor_commands_node')

        self.callback_group = ReentrantCallbackGroup()

        self.twist_subscription = self.create_subscription(
            TwistStamped,
            "/twist",
            self.handle_twist,
            10,
            callback_group=self.callback_group,
        )

        self.motor_speeds_publisher = self.create_publisher(
            MotorSpeeds, 
            "/motor/speeds", 
            10
        )

    def handle_twist(self, msg: TwistStamped):
        x = msg.twist.linear.x
        y = msg.twist.linear.y
        z = msg.twist.linear.z
        pitch = msg.twist.angular.y
        roll = msg.twist.angular.x
        yaw = msg.twist.angular.z
        lastTimestamp = msg.header.stamp
        
        # top left to bottom right for motors
        motorSpeeds = [0]*8
        for i in range(4):
            motorSpeeds[i] += x
        for i in range(4):
            if i == 0 or i == 3:
                motorSpeeds[i] -= y
            else:
                motorSpeeds[i] += y
        for i in range(4):
            motorSpeeds[i+4] += z
        for i in range(4):
            if i == 0 or i == 2:
                motorSpeeds[i] -= yaw
            else:
                motorSpeeds[i] += yaw
        for i in range(4):
            if i == 0 or i == 1:
                motorSpeeds[i+4] -= pitch
            else:
                motorSpeeds[i+4] += pitch
        for i in range(4):
            if i == 0 or i == 2:
                motorSpeeds[i+4] += roll
            else:
                motorSpeeds[i+4] -= roll
        m = 0
        for i in motorSpeeds:
            m = abs(max(m, abs(i)))
        if m > refrenceMaxSpeed:
            for i in range(8):
                motorSpeeds[i] = motorSpeeds[i]/m * refrenceMaxSpeed

        commanded_speeds = MotorSpeeds()
        commanded_speeds.thruster0 = motorSpeeds[0]
        commanded_speeds.thruster1 = motorSpeeds[1]
        commanded_speeds.thruster2 = motorSpeeds[2]
        commanded_speeds.thruster3 = motorSpeeds[3]
        commanded_speeds.thruster4 = motorSpeeds[4]
        commanded_speeds.thruster5 = motorSpeeds[5]
        commanded_speeds.thruster6 = motorSpeeds[6]
        commanded_speeds.thruster7 = motorSpeeds[7]
        commanded_speeds.header.stamp = lastTimestamp

        self.motor_speeds_publisher.publish(commanded_speeds)
        return


def main(args=None):
    rclpy.init(args=args)
    node = MotorSpeedsNode()
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
