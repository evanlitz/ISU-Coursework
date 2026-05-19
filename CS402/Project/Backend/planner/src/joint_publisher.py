#!/usr/bin/env python3
"""
joint_publisher.py  –  Python 3.8 / ROS Noetic

Publishes a single-waypoint joint trajectory goal to the UR10e controller.

Run inside the Docker container after sourcing the workspace:
    source /catkin_ws/devel/setup.bash
    python3 joint_publisher.py

The joint positions below are given in the order the controller expects:
    [shoulder_pan, shoulder_lift, elbow, wrist_1, wrist_2, wrist_3]
All values are in radians.
"""

import rospy
from trajectory_msgs.msg import JointTrajectoryPoint
from control_msgs.msg import FollowJointTrajectoryActionGoal

# ----- Configuration --------------------------------------------------------

GOAL_TOPIC = "/scaled_pos_joint_traj_controller/follow_joint_trajectory/goal"

# Joint names in the order the UR10e controller expects
JOINT_NAMES = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

# Target joint positions (radians)
TARGET_POSITIONS = [1.0, -1.3, 1.8, -1.9, -1.5, 1.0]

# Time allowed for the robot to reach the target (seconds)
MOTION_DURATION = 20.0

# ---------------------------------------------------------------------------


def main():
    rospy.init_node("ur10e_joint_publisher", anonymous=True)

    pub = rospy.Publisher(GOAL_TOPIC, FollowJointTrajectoryActionGoal, queue_size=1)

    # Wait for the controller to subscribe
    rospy.loginfo("Waiting for controller to connect...")
    start = rospy.Time.now()
    while (pub.get_num_connections() == 0
           and (rospy.Time.now() - start).to_sec() < 5.0
           and not rospy.is_shutdown()):
        rospy.sleep(0.05)

    if pub.get_num_connections() == 0:
        rospy.logerr("No subscribers found. Is the UR driver running?")
        return

    # Build the trajectory message
    msg = FollowJointTrajectoryActionGoal()
    now = rospy.Time.now()
    msg.header.stamp = now
    msg.goal_id.stamp = now
    msg.goal_id.id = f"joint_publisher_{now.to_nsec()}"

    msg.goal.trajectory.joint_names = JOINT_NAMES

    point = JointTrajectoryPoint()
    point.positions = TARGET_POSITIONS
    point.time_from_start = rospy.Duration.from_sec(MOTION_DURATION)

    msg.goal.trajectory.points = [point]

    pub.publish(msg)
    rospy.loginfo("Published trajectory goal:")
    for name, pos in zip(JOINT_NAMES, TARGET_POSITIONS):
        rospy.loginfo("  %-25s  %.4f rad", name, pos)
    rospy.loginfo("Motion duration: %.1f seconds", MOTION_DURATION)

    # Wait for motion to complete
    rospy.sleep(MOTION_DURATION + 0.5)
    rospy.loginfo("Done.")


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
