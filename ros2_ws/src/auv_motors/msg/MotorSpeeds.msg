# A list of 8 (one for each thruster) floats to represent motor throttles, -1 for full revese, 0 for stop, and 1 for full forward
# ros2 topic pub -r 10 /motor_commands test_package/msg/MotorSpeeds "{thruster0: 0, thruster1: 1, thruster2: 2, thruster3: 3, thruster4: 4, thruster5: 5, thruster6: 6, thruster7: 7}"
# ros2 topic pub --once /motor_commands test_package/msg/MotorSpeeds "{thruster0: 1, thruster1: 1, thruster2: 2, thruster3: 3, thruster4: 4, thruster5: 5, thruster6: 6, thruster7: 7}"
float64 thruster0
float64 thruster1
float64 thruster2
float64 thruster3
float64 thruster4
float64 thruster5
float64 thruster6
float64 thruster7
time stamp
