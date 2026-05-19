"""
PD Control for Forward Kinematics - UR10e Robot
================================================

This script demonstrates PD (Proportional-Derivative) torque control for direct joint position control.
The robot moves to a desired joint configuration using PD control.
"""

import mujoco as mj
import mujoco.viewer
import numpy as np
import os

# Path to XML model
current_dir = os.path.dirname(os.path.abspath(__file__))
xml_path = os.path.join(current_dir, "ur10e", "ur10e_custom_gripper_scene.xml")

# Control parameters
TIME_STEP = 0.002
KP_JOINTS = np.array([450, 370, 135, 150, 100, 144])   # Proportional gains per joint
KD_JOINTS = np.array([3.5, 30.36, 26.4375, 35, 3.9, 2.86])  
KP_GRIPPER = 17.8  # Proportional gain for gripper
KD_GRIPPER = 2.0   # Derivative gain for gripper
DURATION = 5.0  # Simulation duration
GRIPPER_CLOSE_DURATION = 1.0  # Duration for gripper closing

# Initial and target joint positions (6 DOF for arm)
initial_qpos = np.array([-1.5708, -2.5708, 1.2708, -2.0, 1.5708, 0.0])
target_qpos = np.array([-1.4517, -2.0100, 2.0192, -2.0658, -1.6237, 0.0122])

# Gripper positions (radians)
GRIPPER_OPEN = 1.5   # Open position (minimum)
GRIPPER_CLOSED = -0.17453      # Closed position (slightly less than max 1.74533 for safety)


def pd_control(desired_qpos, current_qpos, current_qvel, kp, kd):
    """
    Compute PD control torques.
    
    Args:
        desired_qpos: Desired joint positions
        current_qpos: Current joint positions
        current_qvel: Current joint velocities
        kp: Proportional gain
        kd: Derivative gain
    
    Returns:
        Control torques
    """
    pos_error = desired_qpos - current_qpos
    vel_error = -current_qvel
    return kp * pos_error + kd * vel_error


def interpolate_qpos(initial, target, alpha):
    """Smooth interpolation between initial and target joint positions."""
    return initial + alpha * (target - initial)


def main():
    model = mj.MjModel.from_xml_path(xml_path)
    data = mj.MjData(model)
    model.opt.timestep = TIME_STEP

    gripper_actuator_id = mj.mj_name2id(model, mj.mjtObj.mjOBJ_ACTUATOR, "gripper")
    gripper_joint_id = mj.mj_name2id(model, mj.mjtObj.mjOBJ_JOINT, "gripper")

    data.qpos[:6] = initial_qpos
    mj.mj_forward(model, data)
    
    print("UR10e PD Control Demo")
    print(f"Initial joint positions: {initial_qpos}")
    print(f"Target joint positions: {target_qpos}")
    
    with mujoco.viewer.launch_passive(model, data) as viewer:
        while viewer.is_running():
            if data.time < DURATION:
                alpha = data.time / DURATION
                smooth_alpha = 3 * alpha**2 - 2 * alpha**3
                desired_qpos = interpolate_qpos(initial_qpos, target_qpos, smooth_alpha)
            else:
                desired_qpos = target_qpos
            
            # Compute PD control torques for arm
            current_qpos = data.qpos[:6]
            current_qvel = data.qvel[:6]
            torques = pd_control(desired_qpos, current_qpos, current_qvel, KP_JOINTS, KD_JOINTS)

            data.ctrl[:6] = torques
            
            # Gripper PD control
            if gripper_actuator_id >= 0 and gripper_joint_id >= 0:
                # Compute desired gripper position
                if data.time < DURATION:
                    desired_gripper_pos = GRIPPER_OPEN
                elif data.time < DURATION + GRIPPER_CLOSE_DURATION:
                    alpha = (data.time - DURATION) / GRIPPER_CLOSE_DURATION
                    smooth_alpha = 3 * alpha**2 - 2 * alpha**3
                    desired_gripper_pos = interpolate_qpos(GRIPPER_OPEN, GRIPPER_CLOSED, smooth_alpha)
                else:
                    desired_gripper_pos = GRIPPER_CLOSED
                
                # PD control for gripper
                qpos_adr = model.jnt_qposadr[gripper_joint_id]
                qvel_adr = model.jnt_dofadr[gripper_joint_id]
                current_gripper_pos = data.qpos[qpos_adr]
                current_gripper_vel = data.qvel[qvel_adr] if qvel_adr >= 0 else 0.0
                gripper_control = pd_control(desired_gripper_pos, current_gripper_pos, current_gripper_vel, KP_GRIPPER, KD_GRIPPER)
                data.ctrl[gripper_actuator_id] = desired_gripper_pos + gripper_control * TIME_STEP
            
            # Step simulation
            mj.mj_step(model, data)
            viewer.sync()
    
    print("Simulation completed")


if __name__ == "__main__":
    main()

