cmake_minimum_required(VERSION 3.8)
project(auv_motors)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)
find_package(rosidl_default_generators REQUIRED)

#### ROS2 Interface Directives ####
set(interface_files
  # Messages/Services/Actions
  "msg/MotorCommands.msg"
)
rosidl_generate_interfaces(${PROJECT_NAME}
  ${interface_files}
  DEPENDENCIES
)
ament_export_dependencies(
  rosidl_default_runtime
)
#### ROS2 Interface Directives [END] ####

install(DIRECTORY
  #launch dir to be added later
  #stonefish may also be added here or in another container
  src
  DESTINATION share/${PROJECT_NAME}/
)

install(DIRECTORY
  #launch dir to be added later
  #stonefish may also be added here or in another container
  src
  DESTINATION share/${PROJECT_NAME}/
)

install(PROGRAMS
  # TODO: add more nodes here
  src/motor_commands.py
  src/uart_manager.py
  DESTINATION lib/auv_motors
)


if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
