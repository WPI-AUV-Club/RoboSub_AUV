FROM ros:jazzy-ros-core

ARG USERNAME=RoboSub #Can change to any name you want
ARG USER_UID=1001
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    #
    # [Optional] Add sudo support. Omit if you don't need to install software after connecting.
    && apt-get update \
    && apt-get install -y \
    sudo \
    dos2unix \
    python3-colcon-common-extensions \
    python3-rosdep \
    git \
    python3-pip \
    build-essential \
    ros-jazzy-pcl-conversions \
    ros-jazzy-pcl-ros \
    && rm -rf /var/lib/apt/lists/* \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# [Optional] Set the default user. Omit if you want to keep the default as root.
USER $USERNAME

# Install python libraries
RUN pip3 install pyserial --break-system-packages
RUN pip3 install Jetson.GPIO --break-system-packages
RUN pip3 install simple-pid --break-system-packages

# Initialize rosdep
RUN sudo rosdep init || true
RUN rosdep update

# Set working directory
WORKDIR /workspaces/RoboSub_AUV

# Copy the ROS2 workspace
COPY ros2_ws ./ros2_ws

# Build the workspace
RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && cd /workspaces/RoboSub_AUV && colcon build --symlink-install"

# Source ROS2 and the workspace in bashrc
RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc \
    && echo "source /workspaces/RoboSub_AUV/install/setup.bash" >> ~/.bashrc

# Make Python scripts executable
RUN find /workspaces/RoboSub_AUV/ros2_ws/src -name "*.py" -exec sudo chmod +x {} \;