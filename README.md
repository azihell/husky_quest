## huskyprj_ws
Husky on a quest for a yellow sphere on CIMATEC school grounds

Here we have a Clearpath modified Husky robot equipped with a Velodyne LiDAR VLP-16 mapping a place while looking for a yellow ball. The LiDAR point cloud is simulated through the [A-LOAM](https://github.com/HKUST-Aerial-Robotics/A-LOAM) package, but it is subsequently reduced to a laser scanning, which is the strategy used on the mapping action.

The robot uses 2D navigation solution [nav2d](http://wiki.ros.org/nav2d_navigator?distro=melodic) along with [GMapping](http://wiki.ros.org/gmapping) to be able to safely move around while looking for a yellow sphere by means of a monocular camera and OpenCV circle detection. By using distance calibration on a known size object, the software can determine the camera distance to the object and then instruct the nav2d package on how to move the robot to the desired location (close to the sphere).
