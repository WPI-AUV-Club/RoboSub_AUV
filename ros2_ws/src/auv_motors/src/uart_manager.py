#!/usr/bin/env python3

from auv_motors.msg import MotorCommands
import rclpy
import math
import serial
import time
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from datetime import datetime
"""
Send out motor commands
"""

class UARTManagerNode(Node):
    def __init__(self):
        super().__init__('uart_manager_node')

        self.callback_group = ReentrantCallbackGroup()

        #Topic Subscription
        self.motor_speed_subscription = self.create_subscription(
            MotorCommands,
            "/motor/speeds",
            self.handle_speeds,
            10,
            callback_group=self.callback_group,
        )

        #Initialize an unique ID for this pico boot cycle
        self.pico_id = self.get_timestamp()

        #Open the serial port
        self.serial_port = serial.Serial(
            port="/dev/ttyTHS1",
            baudrate=38400,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_ODD,
            stopbits=serial.STOPBITS_ONE,
        )
        self.serial_port.reset_input_buffer()

        #Define Variables
        self.time_last_pair_attempted = time.time()
        self.pairing_cooldown_s = 1

        self.msg_buffer = ""
        self.end_of_packet = b'\x00'
        self.prev_ack_index = 0
        self.prev_did_recv_packet = False

        self.full_stop_speed = 128
        self.commanded_speeds = [self.full_stop_speed] * 8

        #Periodic Timer
        self.command_period: float = 0.02
        self.timer = self.create_timer(self.command_period, self.timer_callback)


    #Callbacks
    def timer_callback(self):
        """Method that is periodically called by the timer."""

        did_recv_packet = self.process_msg()

        if(not did_recv_packet and not self.prev_did_recv_packet):
            print("SELF>DID_NOT_RECV_PACKET")
        self.prev_did_recv_packet = did_recv_packet

        self.send_command()

    def handle_speeds(self, msg: MotorCommands):
        """Method that is called when a new msg is received by the node."""
        new_commanded_speeds = [
            msg.thruster0,
            msg.thruster1,
            msg.thruster2,
            msg.thruster3,
            msg.thruster4,
            msg.thruster5,
            msg.thruster6,
            msg.thruster7,
        ]

        #Validate speeds are within expected range
        valid_speeds = True
        for speed in new_commanded_speeds:
            valid_speeds = valid_speeds and speed >= -1 and speed <= 1
        
        if (not valid_speeds):
            self.commanded_speeds = [self.full_stop_speed] * 8
            print("SELF>Improperly formatted commanded speeds")
            return

        #Convert from a -1 to 1 float into a 1 to 255 int
        for speed in new_commanded_speeds:
            speed = math.floor(speed*127+128)

        self.commanded_speeds = new_commanded_speeds
        print("SELF>New Speeds Recv'd")


    #ID/File Ops
    def get_timestamp(self) -> str:
        return datetime.now().strftime("%m/%d/%Y %H:%M:%S")

    #Transmitting
    def send_command(self):
        for i in range(8):
            self.serial_port.write(
                self.commanded_speeds[i].to_bytes(1, byteorder='big')
            )
            
        self.serial_port.write(self.end_of_packet)

    def send_paring_ack(self):
        if (time.time() - self.time_last_pair_attempted > self.pairing_cooldown_s):
            self.pico_id = self.get_timestamp()

            self.serial_port.write(b'ACK:ID')
            self.serial_port.write(self.end_of_packet)

            print("Pico Reboot Detected, assigning new ID")

            self.time_last_pair_attempted = time.time()

    #Receiving
    def process_msg(self):
        have_received_valid_packet = False

        while (self.serial_port.in_waiting > 0):
            new_byte = self.serial_port.read()
            if(new_byte == self.end_of_packet):
                have_received_valid_packet = self.handle_end_of_msg() or have_received_valid_packet
                continue
            
            if "ACK:" in self.msg_buffer:
                self.handle_end_of_ack_msg(new_byte)
            else:
                self.msg_buffer += new_byte.decode("utf-8", errors="replace")
                if "REQ:ID" in self.msg_buffer:
                    self.send_paring_ack()

        return have_received_valid_packet

    def handle_end_of_msg(self):
        valid_packet = False

        if (len(self.msg_buffer) > 0): 
            print(self.pico_id + '>' + self.msg_buffer)
            valid_packet = True

        self.msg_buffer = ""
        return valid_packet

    def handle_end_of_ack_msg(self, new_byte):
        index = int.from_bytes(new_byte, "big")
        if (index != self.prev_ack_index+1 and self.prev_ack_index != 255):
            print("SELF>NONSEQUENTIAL_ACK")

        self.prev_ack_index = index
        self.msg_buffer += str(index)


def main(args=None):
    rclpy.init(args=args)
    node = UARTManagerNode()
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