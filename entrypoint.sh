#!/bin/bash
set -e

# Source ROS2 and RoboSub workspace environments
if [ -f /opt/ros/jazzy/setup.bash ]; then
    source /opt/ros/jazzy/setup.bash
fi

if [ -f /workspaces/RoboSub_AUV/install/setup.bash ]; then
    source /workspaces/RoboSub_AUV/install/setup.bash
fi

exec "$@"
