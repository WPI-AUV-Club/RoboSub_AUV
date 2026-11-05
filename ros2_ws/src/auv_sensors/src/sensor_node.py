import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Vector3
from geometry_msgs.msg import Quaternion

import board
import busio
from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR,
)
from adafruit_bno08x.i2c import BNO08X_I2C


class SensorNode(Node):
    def __init__(self):
        super().__init__('sensor_node')

        self.sensor_raw_publisher = self.create_publisher(
            Imu, 
            "/sensor/data/raw", 
            10
        )
        self.mag_raw_publisher = self.create_publisher(
            Vector3, 
            "/sensor/data/mag", 
            10
        )

        self.i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
        self.bno = BNO08X_I2C(self.i2c)

        self.bno.enable_feature(BNO_REPORT_ACCELEROMETER)
        self.bno.enable_feature(BNO_REPORT_GYROSCOPE)
        self.bno.enable_feature(BNO_REPORT_MAGNETOMETER)
        self.bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

        #Periodic Timer
        self.command_period: float = 0.02
        self.timer = self.create_timer(self.command_period, self.timer_callback)

    
    #Callbacks
    def timer_callback(self):
        # Imu Data
        imu_data = Imu()

        gyro_x, gyro_y, gyro_z = self.bno.gyro
        imu_data.angular_velocity = Vector3(x=gyro_x, y=gyro_y, z=gyro_z)

        accel_x, accel_y, accel_z = self.bno.acceleration
        imu_data.linear_acceleration = Vector3(x=accel_x, y=accel_y, z=accel_z)

        quat_i, quat_j, quat_k, quat_real = self.bno.quaternion
        imu_data.orientation = Quaternion(x=quat_i, y=quat_j, z=quat_k, w=quat_real)

        # Magnetometer Data
        self.sensor_raw_publisher.publish(imu_data)

        mag_x, mag_y, mag_z = self.bno.magnetic
        mag_data = Vector3(x=mag_x, y=mag_y, z=mag_z)
        self.mag_raw_publisher.publish(mag_data)


def main(args=None):
    rclpy.init(args=args)
    node = SensorNode()
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