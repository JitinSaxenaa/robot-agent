import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/jitin-saxena/Projects/robot-agent/ros2_ws/install/robot_bringup'
