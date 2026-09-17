#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Vector3
from test_package.msg import MotorCommands
from simple_pid import PID


class TwistConvNode(Node):
    """A ROS2 Node that converts local frame twists into motor commands."""

    def __init__(self):
        super().__init__('Twist_Conv_Node')

        #Publish to motor commands topic
        self.motor_commands_publisher = self.create_publisher(
            msg_type=MotorCommands,
            topic='/motor_commands',
            qos_profile=1)
        
        #Subscribe to desired twist topic
        self.desired_twist_subscriber = self.create_subscription(
            msg_type=Twist,
            topic='/desired_twist',
            callback=self.desired_twist_subscriber_callback,
            qos_profile=1)
        
        #Variables
        self.MAX_LINEAR_SPEED_X = 1
        self.MAX_LINEAR_SPEED_Y = 1
        self.MAX_LINEAR_SPEED_Z = 1
        self.MAX_ANGULAR_SPEED_X = 1
        self.MAX_ANGULAR_SPEED_Y = 1
        self.MAX_ANGULAR_SPEED_Z = 1

        self.target_vels = Twist()
        self.battery_v = 12.0

        #Yaw axis is the only with a PID as its the only one with a feedback loop. The other axes are open loop
        self.yaw_pid = PID(1, 0, 0, setpoint=0)
        self.altitude_pid = PID(1, 0, 0, setpoint=0)

        #Periodic Timer
        self.command_period: float = 0.02
        self.timer = self.create_timer(self.command_period, self.timer_callback)


    #Callbacks
    def timer_callback(self):
        """Method that is periodically called by the timer."""
        
        thrusts_kg = self.get_thrusts_kg(self.target_linear_vels)
        motor_speeds = self.get_motor_commands(thrusts_kg, self.battery_v) #TODO: Get battery voltage from a topic

        self.motor_commands_publisher.publish(motor_speeds)


    def desired_twist_subscriber_callback(self, msg: Twist):
        """Method that is called when a new msg is received by the node."""
        new_vels = Twist()
        
        new_vels.linear.x = self.clamp(msg.linear.x, self.MAX_LINEAR_SPEED_X)
        new_vels.linear.y = self.clamp(msg.linear.y, self.MAX_LINEAR_SPEED_Y)
        new_vels.linear.z = self.clamp(msg.linear.z, self.MAX_LINEAR_SPEED_Z)

        new_vels.angular.x = self.clamp(msg.angular.x, self.MAX_ANGULAR_SPEED_X)
        new_vels.angular.y = self.clamp(msg.angular.y, self.MAX_ANGULAR_SPEED_Y)
        new_vels.angular.z = self.clamp(msg.angular.z, self.MAX_ANGULAR_SPEED_Z)

        self.target_vels = new_vels
    

    #Util Function
    def clamp(self, n, max_abs_val):
        return max(-max_abs_val, min(n, max_abs_val))
    

    #Motor Conversions
    def get_thrusts_kg(self, vel_mps: Twist):
        """Convert the desired linear velocity in m/s to a thrust value in kg."""
        """TODO: Charecterize behavior to determine these equations. For now, we will incorrectly assume a linear relationship between desired velocity and thrust."""
        thrusts_kg = Twist()

        thrusts_kg.linear.x = vel_mps.linear.x/self.MAX_LINEAR_SPEED_X
        thrusts_kg.linear.y = vel_mps.linear.y/self.MAX_LINEAR_SPEED_Y
        thrusts_kg.linear.z = vel_mps.linear.z/self.MAX_LINEAR_SPEED_Z

        thrusts_kg.angular.x = vel_mps.angular.x/self.MAX_ANGULAR_SPEED_X
        thrusts_kg.angular.y = vel_mps.angular.y/self.MAX_ANGULAR_SPEED_Y
        thrusts_kg.angular.z = vel_mps.angular.z/self.MAX_ANGULAR_SPEED_Z

        return thrusts_kg

    def get_motor_speed(thrust_kg, batt_v):
        """References a 3d surface of best fit to determine the nessecary motor speed to achive the desired thrust at the current battery voltage."""
        """Motor speed is given as a value from -1 to 1"""
        x = thrust_kg
        y = batt_v
        """Coefficients were determined by values in the datasheet, discontinuity at low thrusts nessecitates a seperate positive and negative surface of best fit."""
        if (thrust_kg == 0):
            return 0
        elif (thrust_kg > 0):
            a,b,c,d,e,f = 0.80159994,0.4042657,-0.09132469,-0.01855475,0.00281378,-0.00812859
        else:
            a,b,c,d,e,f = -0.78689061,0.51407952,0.08920133,0.02886842,-0.00272574,-0.01048958
        return a + b*x + c*y + d*x**2 + e*y**2 + f*x*y

    def get_motor_commands(self, thrusts_kg: Twist):
        """Given a twist of thrust in each direcection (For example, thrusts_kg.linear.x is the thrust for each motor in the x direction)
        Output an array of motor commands."""

        motor_commands = MotorCommands()

        forward_speed = self.get_motor_speed(thrusts_kg.linear.x, self.battery_v)
        strafe_speed = self.get_motor_speed(thrusts_kg.linear.y, self.battery_v)
        vertical_speed = self.get_motor_speed(thrusts_kg.linear.z, self.battery_v)

        yaw_thrust = self.get_motor_speed(thrusts_kg.angular.z, self.battery_v)
        pitch_thrust = self.get_motor_speed(thrusts_kg.angular.y, self.battery_v)
        roll_thrust = self.get_motor_speed(thrusts_kg.angular.x, self.battery_v)

        #TODO: Make these correspond to the actual robot
        #Forward Facing Thrusters
        motor_commands.thruster0 =  forward_speed + yaw_thrust - strafe_speed
        motor_commands.thruster1 =  forward_speed - yaw_thrust + strafe_speed
        motor_commands.thruster2 = -forward_speed + yaw_thrust + strafe_speed
        motor_commands.thruster3 = -forward_speed - yaw_thrust - strafe_speed

        #Downward facing thrusters
        motor_commands.thruster0 = vertical_speed + roll_thrust - pitch_thrust
        motor_commands.thruster1 = vertical_speed + roll_thrust + pitch_thrust
        motor_commands.thruster2 = vertical_speed - roll_thrust - pitch_thrust
        motor_commands.thruster3 = vertical_speed - roll_thrust + pitch_thrust

        return motor_commands


def main(args=None):
    """
    The main function.
    :param args: Not used directly by the user, but used by ROS2 to configure
    certain aspects of the Node.
    """
    try:
        rclpy.init(args=args)

        twist_conv_node = TwistConvNode()
        rclpy.spin(twist_conv_node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()

