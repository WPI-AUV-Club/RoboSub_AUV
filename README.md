Test code to confirm ROS2 nodes working within docker container  

prerequisites:
Docker

Makes sure to follow post install steps from docker page on linux  

To run follow the following steps  

Pull repo  
CD into repo  
docker build . -t auv:latest  (optionally right click on file and click build image in vscode (need docker extension for this. This command constructs the container))  
docker run -it auv:latest  (this actually runs it and enters the container in the terminal)  

you should see something like RoboSub@(hex string):/workspace/RoboSub#  
you can now run the ros node

ros2 run test_package test_node.py  
