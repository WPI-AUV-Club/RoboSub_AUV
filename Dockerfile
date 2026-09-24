FROM ros:jazzy-ros-core

# Install system and ROS 2 dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    sudo \
    dos2unix \
    python3-colcon-common-extensions \
    python3-rosdep \
    git \
    python3-pip \
    build-essential \
    python3-serial \
    ros-jazzy-pcl-conversions \
    ros-jazzy-pcl-ros \
    ros-jazzy-foxglove-bridge \
    ros-jazzy-rosidl-default-generators \
    ros-jazzy-rosidl-default-runtime \
    ros-jazzy-geometry-msgs \
    ros-jazzy-std-msgs \
    ros-jazzy-rclpy \
    ros-jazzy-rclcpp \
    && rm -rf /var/lib/apt/lists/*

# Install python libraries for hardware interface
RUN pip3 install --no-cache-dir --break-system-packages \
    pyserial \
    Jetson.GPIO \
    simple-pid

# Set working directory
WORKDIR /workspaces/RoboSub_AUV

# Copy ROS2 workspace and entrypoint
COPY ros2_ws ./ros2_ws
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Make Python scripts executable before colcon build
RUN find /workspaces/RoboSub_AUV/ros2_ws/src -name "*.py" -exec chmod +x {} \;

# Build the workspace
RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && cd /workspaces/RoboSub_AUV && colcon build --symlink-install"

# Source ROS2 and workspace in bashrc for interactive shells
RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc \
    && echo "source /workspaces/RoboSub_AUV/install/setup.bash" >> ~/.bashrc

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]