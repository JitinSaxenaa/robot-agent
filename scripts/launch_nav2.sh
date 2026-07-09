#!/bin/bash
source /opt/ros/jazzy/setup.bash
source ~/Projects/robot-agent/ros2_ws/install/setup.bash
ros2 launch nav2_bringup bringup_launch.py \
  map:=/opt/ros/jazzy/share/turtlebot3_navigation2/map/map.yaml \
  params_file:=/home/jitin-saxena/Projects/robot-agent/config/burger_fixed.yaml \
  use_sim_time:=True autostart:=True use_composition:=False
