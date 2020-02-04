## huskyprj_ws
Husky on a quest for a yellow sphere on CIMATEC school grounds

Here we have a Clearpath modified Husky robot equipped with a Velodyne LiDAR VLP-16 mapping a place while looking for a yellow ball. The LiDAR point cloud is simulated through the [A-LOAM](https://github.com/HKUST-Aerial-Robotics/A-LOAM) package, but it is subsequently reduced to a laser scanning, which is the strategy used on the mapping action.

The robot uses 2D navigation solution [nav2d](http://wiki.ros.org/nav2d_navigator?distro=melodic) along with [GMapping](http://wiki.ros.org/gmapping) to be able to safely move around while looking for a yellow sphere by means of a monocular camera and OpenCV circle detection. By using distance calibration on a known size object, the software can determine the camera distance to the object and then instruct the nav2d package on how to move the robot to the desired location (close to the sphere).

Firstly, launch the <i>cimatec_map huskyplus.launch</i> - the Gazebo with the robot will be generated. Then <i>navi aloam_for_mapping.launch</i>. This one will launch the RViz with the robot and make the laser scan visible. The mapped is represented by the grey area, and the route and collision avoiding is managed by the nav2d package. Some fine tuning is in place to make the robot more efficient in the scenario in case.

The yellow sphere is identified as a target as soon as the distance between it and the robot becomes 20 meters or less (this can be found on <i>leomission.py</i>. This limit was deliberately applied to ensure the navigation won't make the robot stop.
