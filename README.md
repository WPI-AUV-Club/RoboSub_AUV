Test code to confirm ROS2 nodes working within docker container  

prerequisites:
Docker
git lfs

Makes sure to follow post install steps from docker page on linux  

To see the sim gui you may need a X server, to display x11 apps from the container.
There are mutiple ways to do this, you can pick any of them. 

To run follow the following steps  

Pull repo  
CD into repo  

docker compose up -d --build robosub
docker compose run robosub 

you should see something like RoboSub@(hex string or docker desktop):/workspace/RoboSub_Auv#  
you can now run the ros node
ros2 run test_package test_node.py  

Sim test:
ros2 launch simulation robosub_sim.launch.p

Run colcon build --symlink-install and source install/setup.bash everytime you add a new file or if you code it in C++

type exit to leave the container or ctrl C 3 times
Then docker compose down robosub to remove the container