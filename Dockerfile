FROM ros:jazzy-ros-base

ARG USERNAME=RoboSub
ARG USER_UID=1001
ARG USER_GID=$USER_UID

RUN apt-get clean && rm -rf /var/lib/apt/lists
RUN apt update

RUN apt-get update && apt-get install -y curl gnupg2 lsb-release


# Create user and install packages
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get install -y \
        sudo \
        dos2unix \
        python3-colcon-common-extensions \
        python3-rosdep \
        git \
        build-essential \
        ros-jazzy-pcl-conversions \
        ros-jazzy-pcl-ros \
	    libglm-dev \
    	libsdl2-dev \
    	libfreetype6-dev \
    	libglew-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME

RUN sudo rosdep init || true
RUN rosdep update

WORKDIR /workspaces/RoboSub_AUV
RUN sudo apt-get update 
COPY ros2_ws ./ros2_ws


ENV CMAKE_PREFIX_PATH=/usr/local:$CMAKE_PREFIX_PATH

RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash" 

RUN sudo git clone https://github.com/patrykcieslak/stonefish.git && \
    cd stonefish && \
    sudo mkdir build && \
    cd build && \
    sudo cmake .. && \
    sudo make -j$(nproc) && \
    sudo make install && \
    sudo ldconfig

# Install dependencies
RUN rosdep install --from-paths ./ros2_ws/src --ignore-src -r -y

# Build the workspace
RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && cd /workspaces/RoboSub_AUV && colcon build --symlink-install --parallel-workers 1"

# Source ROS2 and the workspace in bashrc
RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc \
    && echo "source /workspaces/RoboSub_AUV/install/setup.bash" >> ~/.bashrc

# Make Python scripts executable
RUN find /workspaces/RoboSub_AUV/ros2_ws/src -name "*.py" -exec sudo chmod +x {} \;

