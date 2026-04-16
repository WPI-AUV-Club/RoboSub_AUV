FROM ros:jazzy-ros-base

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
    build-essential \
    libfreetype6-dev \
    libglm-dev \
    libsdl2-dev \
    libfreetype6-dev \
    ros-jazzy-pcl-conversions \ 
    ros-jazzy-image-transport \ 
    ros-jazzy-geometry-msgs \
    ros-jazzy-sensor-msgs \
    ros-jazzy-tf2 \
    ros-jazzy-tf2-ros \
    && rm -rf /var/lib/apt/lists/* \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Set the default user. Omit if you want to keep the default as root.
USER $USERNAME


# Initialize rosdep
RUN sudo rosdep init || true
RUN rosdep update


# Set working directory
WORKDIR /workspaces/RoboSub_AUV

# Copy the ROS2 workspace
COPY ros2_ws ./ros2_ws

RUN git clone https://github.com/patrykcieslak/stonefish.git \ 
    && cd stonefish \ 
    && mkdir build \ 
    && cd build \ 
    && cmake .. \ 
    && make -j1 \ 
    && sudo make install

# Install dependencies
RUN rosdep install --from-paths ./ros2_ws/src --ignore-src -r -y

# Build the workspace
RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && cd /workspaces/RoboSub_AUV && colcon build --symlink-install --parallel-workers 1"

# Source ROS2 and the workspace in bashrc
RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc \
    && echo "source /workspaces/RoboSub_AUV/install/setup.bash" >> ~/.bashrc

# Make Python scripts executable
RUN find /workspaces/RoboSub_AUV/ros2_ws/src -name "*.py" -exec sudo chmod +x {} \;
