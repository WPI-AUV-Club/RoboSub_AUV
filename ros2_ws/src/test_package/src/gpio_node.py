#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import Jetson.GPIO as GPIO
from GPIO.msg import input_state, output_state #i think imports got some issues
import time
from rclpy.callback_groups import ReentrantCallbackGroup


class GPIO_node(Node):
    """A ROS2 Node that manages GPIO pins on the Jetson."""

    def __init__(self):
        super().__init__('GPIO_node')

        # callback group to allow for multithreading
        self.cb_group = ReentrantCallbackGroup()

        # publisher
        self.ouput_publisher = self.create_publisher(
            output_state,
            "gpio/output",
            1
        )

        # subscription
        self.input_subscription = self.create_subscription(
            input_state,
            "/gpio/input",
            self.handle_input,
            10,
            callback_group=self.cb_group,
        )

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(18, GPIO.OUT)

        # for pwm testing
        while False:
            print("High!")
            GPIO.output(7, GPIO.HIGH)
            time.sleep(1)
            print("Low!")
            GPIO.output(7, GPIO.LOW)
            time.sleep(1)

        self.get_logger().info("gpio node intialized")

    def handle_input(self, input):
        """ Handle GPIO inputs """
        pass

def main(args=None):
    """
    The main function.
    :param args: Not used directly by the user, but used by ROS2 to configure
    certain aspects of the Node.
    """
    try:
        rclpy.init(args=args)

        gpio_node = GPIO_node()
        rclpy.spin(gpio_node)
    except KeyboardInterrupt:
        GPIO.cleanup()
        pass
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()

#test git commit 