# UR10e Robot Demo

This folder contains demo code for controlling the UR10e robot arm with SO101 gripper using MuJoCo.

## Files

- `deploy.py`: Forward kinematics PD control with gripper - controls joint positions and gripper using PD control
- `deploy_ik.py`: Inverse kinematics control - controls end-effector pose using IK + PD torque control
- `generic_ik_solver.py`: Generic IK solver implementation


## Usage

### Forward Kinematics Control with Gripper

Control joint positions and gripper:

```bash
python deploy.py
```

This moves the robot from an initial joint configuration to a target configuration using PD control. The gripper starts open and closes after the arm reaches the target position.

### Inverse Kinematics Control

Control end-effector pose:

```bash
python deploy_ik.py
```

This solves IK for a target end-effector pose and uses PD control to move the joints to the IK solution.

## Gripper Control

The UR10e robot is equipped with an SO101 gripper. In `deploy.py`, the gripper is controlled as follows:

1. **Gripper actuator name**: `"gripper"`
2. **Gripper joint name**: `"gripper"`
3. **Position range**: 
   - Open: `GRIPPER_OPEN = 1.5` radians
   - Closed: `GRIPPER_CLOSED = -0.17453` radians
4. **Control method**: Position actuator with PD control
5. **Control parameters**:
   - `KP_GRIPPER = 17.8`
   - `KD_GRIPPER = 2.0`
   - `GRIPPER_CLOSE_DURATION = 1.0` seconds

### Example: Controlling the Gripper

```python
# Get gripper actuator and joint IDs
gripper_actuator_id = mj.mj_name2id(model, mj.mjtObj.mjOBJ_ACTUATOR, "gripper")
gripper_joint_id = mj.mj_name2id(model, mj.mjtObj.mjOBJ_JOINT, "gripper")

# Get current gripper state
qpos_adr = model.jnt_qposadr[gripper_joint_id]
current_gripper_pos = data.qpos[qpos_adr]

# Set desired gripper position (using position actuator)
data.ctrl[gripper_actuator_id] = desired_gripper_pos
```

The gripper uses a position actuator, so you can directly set the desired position in `data.ctrl[gripper_actuator_id]`. For smoother control, PD control can be applied as shown in `deploy.py`.

## Parameters

You can modify the control parameters in each script:
- `KP_JOINTS`: Proportional gains for arm joints (array of 6 values)
- `KD_JOINTS`: Derivative gains for arm joints (array of 6 values)
- `KP_GRIPPER`: Proportional gain for gripper (default: 17.8)
- `KD_GRIPPER`: Derivative gain for gripper (default: 2.0)
- `DURATION`: Simulation duration in seconds (default: 5.0)
- `GRIPPER_CLOSE_DURATION`: Duration for gripper closing (default: 1.0)
- `TIME_STEP`: Simulation timestep (default: 0.002)

## Notes

- The UR10e robot has 6 DOFs for the arm
- Model file: `ur10e/ur10e_custom_gripper_scene.xml`
- End-effector site name: `attachment_site`
- The gripper is controlled separately from the arm joints
