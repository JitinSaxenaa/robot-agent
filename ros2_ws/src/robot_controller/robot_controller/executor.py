# executor.py
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.parameter import Parameter

from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from tf_transformations import quaternion_from_euler

from .mission_manager import MissionManager


class Executor(Node):

    def __init__(self):
        super().__init__("executor")

        self.declare_parameter("prompt", "Go to A")
        self.prompt = self.get_parameter("prompt").get_parameter_value().string_value

        self.set_parameters([Parameter("use_sim_time", Parameter.Type.BOOL, True)])

        self._action_client = ActionClient(self, NavigateToPose, "navigate_to_pose")

        self.manager = MissionManager()
        self.mission = None
        self.current_index = 0

        self.get_logger().info("Executor Ready")

        # defer mission start until after construction/discovery settle
        self._start_timer = self.create_timer(1.0, self._start_mission)

    def _start_mission(self):
        self._start_timer.cancel()

        self.mission = self.manager.get_mission(self.prompt)
        self.get_logger().info(
            f"Mission received with {len(self.mission.waypoints)} waypoint(s)"
        )
        self.current_index = 0
        self._send_next_goal()

    def _send_next_goal(self):
        if self.current_index >= len(self.mission.waypoints):
            self.get_logger().info("Mission Complete")
            return

        waypoint = self.mission.waypoints[self.current_index]
        self.get_logger().info(
            f"Executing waypoint {self.current_index + 1}/{len(self.mission.waypoints)}"
        )

        if not self._action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error("navigate_to_pose action server not available")
            return

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = self._make_pose(waypoint)

        send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self._feedback_cb
        )
        send_goal_future.add_done_callback(self._goal_response_cb)

    def _make_pose(self, waypoint):
        pose = PoseStamped()
        pose.header.frame_id = "map"
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = waypoint.x
        pose.pose.position.y = waypoint.y
        pose.pose.position.z = 0.0

        q = quaternion_from_euler(0.0, 0.0, waypoint.yaw)
        pose.pose.orientation.x = q[0]
        pose.pose.orientation.y = q[1]
        pose.pose.orientation.z = q[2]
        pose.pose.orientation.w = q[3]
        return pose

    def _feedback_cb(self, feedback_msg):
        eta = feedback_msg.feedback.estimated_time_remaining
        self.get_logger().info(f"ETA: {eta.sec}s")

    def _goal_response_cb(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Goal Rejected — Mission Failed")
            return

        self.get_logger().info("Goal Accepted")
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._result_cb)

    def _result_cb(self, future):
        self.get_logger().info("Waypoint Reached")
        self.current_index += 1
        self._send_next_goal()


def main(args=None):
    rclpy.init(args=args)
    node = Executor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()