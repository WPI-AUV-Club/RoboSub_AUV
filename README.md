# WPI RoboSub AUV - Jetson Docker Stack

## Network & SSH Setup

The laptop and Jetson connect over a dedicated USB-to-Ethernet interface:

* Laptop IP: `192.168.1.1/24`
* Jetson IP: `192.168.1.50/24`
* Foxglove Bridge Port: `8765`

### 1. Network Interface Setup
Assigns the static IP to the USB Ethernet interface, brings it up, and enables NAT masquerading so the Jetson can access the internet through the laptop Wi-Fi:

```bash
./setup_network.sh
```

### 2. Passwordless SSH Setup
Generates an SSH key (if not already present), installs the public key on the Jetson, adds a `jetson` host entry to `~/.ssh/config`, and configures the Docker context:

```bash
./scripts/setup_ssh.sh
```

Once configured, connect directly with:
```bash
ssh jetson
```

---

## Build and Deployment

### Option 1: Native Jetson Build (Online / Internet Sharing)
Streams the source tree to the Jetson Docker daemon over SSH. Builds natively on ARM64 using cached layers:

```bash
./deploy.sh             # Build image and run container in background
./deploy.sh build       # Build image only
./deploy.sh run         # Start container with hardware devices
./deploy.sh shell       # Open interactive shell in container
./deploy.sh test        # Run ROS 2 smoke tests
./deploy.sh stop        # Stop container
./deploy.sh logs        # View container logs
```

### Option 2: Offline Cross-Compilation (Laptop Build)
If the Jetson has no internet routing, the laptop cross-compiles the ARM64 image using Docker Buildx and transfers it over the wire:

```bash
./deploy.sh cross-deploy  # Cross-compile ARM64 on laptop, transfer over wire, and deploy
./deploy.sh cross-run     # Cross-compile, deploy, and enter interactive container
./deploy.sh cross-build   # Cross-compile on laptop without transferring
```

---

## Script Reference (`scripts/`)

| Script | Action |
| :--- | :--- |
| `scripts/setup_network.sh` | Configures USB Ethernet interface (192.168.1.1) and NAT |
| `scripts/setup_ssh.sh` | Configures passwordless SSH key, `~/.ssh/config`, and Docker context |
| `scripts/build.sh` | Builds `auv:latest` natively on the Jetson |
| `scripts/deploy.sh` | Builds on Jetson and starts `auv_core` in background |
| `scripts/run.sh` | Runs container with UART and GPIO devices attached |
| `scripts/build_and_run.sh` | Builds on Jetson and opens interactive shell |
| `scripts/cross_build.sh` | Cross-compiles `linux/arm64` image locally on laptop |
| `scripts/cross_deploy.sh` | Cross-compiles on laptop and streams to hard-wired Jetson |
| `scripts/cross_build_and_run.sh` | Cross-compiles, streams, and enters container |
| `scripts/shell.sh` | Attaches bash shell to running `auv_core` container |
| `scripts/ssh.sh` | Connects to Jetson host over SSH (`ssh jetson`) |
| `scripts/test.sh` | Verifies ROS 2 packages, messages, and hardware libraries |

---

## Hardware Passthrough

The container passes through the following devices:

* UART: `/dev/ttyTHS1` (motor controller communication at 38400 baud)
* GPIO: `/dev/gpiochip0`, `/dev/gpiochip1` (direct hardware GPIO access)
* Network: `--net=host` (DDS discovery and Foxglove WebSocket server on port 8765)

---

## ROS 2 Packages

* `auv_motors`: Thruster controls and UART serial manager (`uart_manager.py`, `motor_commands.py`)
  * Interfaces: `auv_motors/msg/MotorCommands`, `auv_motors/msg/MotorSpeeds`
* `auv_camera`: Camera drivers and vision pipeline (`camera_sensor.py`, `camera_processing.py`, `object_detection.py`)
* `auv_planning`: State machine, path planning, and controls (`state_machine.py`, `path_planning.py`, `controls.py`, `localization.py`)
* `auv_sensors`: Sensor acquisition and filtering (`sensor_node.py`, `leak_sensor.py`, `sensor_filtering.py`)

Run nodes from inside the container:
```bash
ros2 run auv_motors uart_manager.py
ros2 run auv_motors motor_commands.py
```

Sim test:
ros2 launch simulation robosub_sim.launch.p

Run colcon build --symlink-install and source install/setup.bash everytime you add a new file or if you code it in C++

type exit to leave the container or ctrl C 3 times
Then docker compose down robosub to remove the container