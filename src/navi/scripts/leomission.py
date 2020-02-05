#!/usr/bin/env python2.7

# Python packages used:
import os
import cv2
import math
import time
import rospy
import numpy as np
# Importing objects from subpackage "msg" inside "std_msgs"
from std_msgs.msg import Int32, String
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from actionlib_msgs.msg import GoalID 
from geometry_msgs.msg import PoseStamped, Twist, Vector3
#CvBridge is a ROS library that provides an interface between ROS and OpenCV image information.
from cv_bridge import CvBridge, CvBridgeError
from move_base_msgs.msg import MoveBaseActionGoal
from nav2d_navigator.msg import GetFirstMapActionGoal, ExploreActionGoal

class Camera: 
  timer_flag = None

  def __init__(self):
    # node killer
    self.kill = False
    # flag var
    self.flag = True
     # focal length
    self.focalLength = 838.9544

    # Object that acts as a bridge, converting OpenCV messages
    self.bridge = CvBridge()
    # timer var
    self.start = time.time()
    
    # Creation of a node called 'node_camera_mission'
    rospy.init_node('node_camera_mission', anonymous=True)

    # This object publishes a message called "image_pub" to the 'camera/mission' topic using a message type "Image", and has a buffer of size 10, meaning it stores up to 10 messages, in case the subscriber can't get them quickly enough:

    self.image_pub = rospy.Publisher('camera/mission', Image, queue_size=10)
    # move_base publisher object
    self.move_base_pub = rospy.Publisher("/move_base_simple/goal", PoseStamped, queue_size=1) 
    # EXPLORATION THINGS
    self.start_map = rospy.Publisher("/GetFirstMap/goal", GetFirstMapActionGoal, queue_size=1)
    self.start_explore = rospy.Publisher("/Explore/goal", ExploreActionGoal, queue_size = 1)
    self.cancel_map = rospy.Publisher("/GetFirstMap/cancel", GoalID, queue_size = 1)
    self.cancel_explore = rospy.Publisher("/Explore/cancel", GoalID, queue_size = 1)
    time.sleep(1)
    self.start_map.publish()
    time.sleep(10)
    self.cancel_map.publish()
    time.sleep(2)
    self.start_explore.publish()

  def callback(self, data):
    # setup timer and font
    timer = int(time.time() - self.start)
    font = cv2.FONT_HERSHEY_SIMPLEX

    # convert img to cv2
    cv2_frame = self.bridge.imgmsg_to_cv2(data, "bgr8")

    ### COLOR DETECTION ###
    # define range of yellow color
    yellowLower = (20, 100, 100)
    yellowUpper = (32, 255, 255)

    # hsv color-space convert
    hsv = cv2.cvtColor(cv2_frame, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to get only blue colors
    maskYellow = cv2.inRange(hsv, yellowLower, yellowUpper)

    # erosion and dilation for noise removal
    maskYellow = cv2.erode(maskYellow, None, iterations=2)
    maskYellow = cv2.dilate(maskYellow, None, iterations=2) 

    # find contours of image (cv2.CHAIN_APPROX_SIMPLE is for memory saves)
    cnt_yellow = cv2.findContours(maskYellow.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    
    ### CIRCLE DETECTION ###    
    contours_poly = []
    centers = []
    radius = []     
    
    # approximate contours to polygons + get bounding rects and circles
    for index, obj_cnt in enumerate(cnt_yellow):
      contours_poly.append(cv2.approxPolyDP(obj_cnt, 0.009 * cv2.arcLength(obj_cnt, True), True))
      aux1, aux2 = cv2.minEnclosingCircle(contours_poly[index])
      centers.append(aux1)
      radius.append(aux2)
      ## if the camera find the sphere ##
      if(len(contours_poly[index]) > 10):
        # draw a circle in sphere and put a warning message
        cv2.circle(cv2_frame, (int(centers[index][0]), int(centers[index][1])), int(radius[index]), (0, 0, 255), 5)
      # cv2.putText(cv2_frame, 'BOMB HAS BEEN DETECTED!', (20, 130), font, 2, (0, 0, 255), 5)
        
        if self.goal_move_base(centers[0][0], radius[0]) and not self.kill:     
          os.system('rosnode kill /Operator')
          #time.sleep(3)
          self.kill = True
 
        ### MOVE BASE GOAL ###
        
            
    # merge timer info to frame
    cv2.putText(cv2_frame, str(timer) + 's', (20, 60), font, 2, (50, 255, 50), 5) 
    cv2.putText(cv2_frame, str(time.ctime()), (10, 700), font, 2, (50, 255, 50), 6)

    # convert img to ros and pub image in a topic
    ros_frame = self.bridge.cv2_to_imgmsg(cv2_frame, "bgr8")
    self.image_pub.publish(ros_frame)

  def listener(self):
    # subscribe to a topic
    rospy.Subscriber('/husky_cam/image_raw', Image, self.callback)  
    # simply keeps python from exiting until this node is stopped
    rospy.spin()
  
  def goal_move_base(self, center_ball, radius):
    distance = (1 * self.focalLength) / (radius * 2)
    rospy.loginfo(distance)
    if distance >= 20:
      # rospy.loginfo("Distancia euclidiana maior que 20 m")
      return False
    # rospy.loginfo("Fim da exploracao - alvo travado")
    self.cancel_explore.publish()     

    
    y_move_base = -(center_ball - 640) / (radius*2) 
    if abs(y_move_base) < 0.006:
      x_move_base = distance
    else:
      x_move_base = math.sqrt(distance**2 - y_move_base**2)
    
    # setup pub values with x and y positions
    msg_move_to_goal = PoseStamped()
    msg_move_to_goal.pose.position.x = x_move_base - 3
    msg_move_to_goal.pose.position.y = y_move_base
    msg_move_to_goal.pose.orientation.w = 1
    msg_move_to_goal.header.frame_id = 'real_cam'
    rospy.loginfo(msg_move_to_goal)
    # pub a best rout to move base if distance is < 4m
    if self.flag and (distance > 4):       
      self.move_base_pub.publish(msg_move_to_goal)
      self.flag = False
      self.timer_flag = time.time()
    if time.time() - self.timer_flag > 5:
      self.flag = True
    return True
    # print information for debug
    # print('BOMB HAS BEEN DETECTED')
    # print('DISTANCIA EM LINHA: ' + str(distance))  # ISSO FICA LOUCO COM A PROXIMIDADE
    # print('INCREMENTO X: ' + str(x_move_base))
    # print('INCREMENTO Y: ' + str(y_move_base))
    # print('##################################')

# main function
if __name__	== '__main__':
  try:
    cam_print = Camera()  
    cam_print.listener()  
  except rospy.ROSInterruptException:
    pass
