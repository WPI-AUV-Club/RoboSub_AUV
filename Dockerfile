FROM ros:jazzy-ros-core

# Create the user
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    sudo \
    dos2unix \
    python3-colcon-common-extensions \
    python3-rosdep \
    git \
    python3-pip \
    build-essential \
    ros-jazzy-pcl-conversions \
    ros-jazzy-pcl-ros \
    ros-$ROS_DISTRO-foxglove-bridge \
    && rm -rf /var/lib/apt/lists/*

# Install python libraries
RUN pip3 install --no-cache-dir --break-system-packages \
    pyserial \
    Jetson.GPIO \
    simple-pid

# only if you actually rosdep install somewhere
# RUN rosdep update   

# Set working directory
WORKDIR /workspaces/RoboSub_AUV

# Copy the ROS2 workspace
COPY ros2_ws ./ros2_ws

# Build the workspace
RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && cd /workspaces/RoboSub_AUV && colcon build --symlink-install --parallel-workers 1"

# Source ROS2 and workspace in bashrc for interactive shells
RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc \
    && echo "source /workspaces/RoboSub_AUV/install/setup.bash" >> ~/.bashrc

<<<<<<< HEAD
# Make Python scripts executable
RUN find /workspaces/RoboSub_AUV/ros2_ws/src -name "*.py" -exec chmod +x {} \;