Test code to confirm ROS2 nodes working within docker container  

prerequisites:
Docker
git lfs

Makes sure to follow post install steps from docker page on linux  

To run follow the following steps  

Pull repo  
CD into repo  

docker compose build robosub 
docker compose run robosub 

you should see something like RoboSub@(hex string):/workspace/RoboSub#  
you can now run the ros node

ros2 run test_package test_node.py  
Run colcon build --symlink-install and source install/setup.bash everytime you add a new file or if you code it in C++

