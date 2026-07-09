import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from tf_transformations import quaternion_from_euler


class Nav2Client(Node):

    def __init__(self):
        super().__init__("nav2_client")

        self.client = ActionClient(
            self,
            NavigateToPose,
            "navigate_to_pose",
        )

        self.get_logger().info("Nav2 Client Ready")

    def navigate_to_pose(self, waypoint):

        self.client.wait_for_server()

        goal = NavigateToPose.Goal()

        goal.pose = PoseStamped()

        goal.pose.header.frame_id = "map"
        goal.pose.header.stamp = self.get_clock().now().to_msg()

        goal.pose.pose.position.x = waypoint.x
        goal.pose.pose.position.y = waypoint.y
        goal.pose.pose.position.z = 0.0

        q = quaternion_from_euler(0.0, 0.0, waypoint.yaw)

        goal.pose.pose.orientation.x = q[0]
        goal.pose.pose.orientation.y = q[1]
        goal.pose.pose.orientation.z = q[2]
        goal.pose.pose.orientation.w = q[3]

        self.get_logger().info(
            f"Sending goal ({waypoint.x}, {waypoint.y})"
        )

        future = self.client.send_goal_async(goal)

        rclpy.spin_until_future_complete(self, future)

        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error("Goal Rejected")
            return False

        self.get_logger().info("Goal Accepted")

        result_future = goal_handle.get_result_async()

        rclpy.spin_until_future_complete(self, result_future)

        self.get_logger().info("Goal Reached")

        return True