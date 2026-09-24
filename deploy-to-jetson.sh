sudo docker buildx build --platform linux/arm64 -t auv:latest --load . && \
sudo docker save auv:latest | gzip | sudo ssh jetson@192.168.1.50 "gunzip | docker load" && \
ssh -t jetson@192.168.1.50 "docker run -it --entrypoint /bin/bash --device=/dev/ttyTHS1:/dev/ttyTHS1 --device=/dev/gpiochip0:/dev/gpiochip0 --device=/dev/gpiochip1:/dev/gpiochip1 --group-add $(stat -c '%g' /dev/gpiochip0) --privileged -p 8765:8765 auv:latest"

# ros2 run auv_motors uart_manager.py

# may need to be ran once:
# docker run --privileged --rm tonistiigi/binfmt --install all
