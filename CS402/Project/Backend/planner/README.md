# planner

ROS + MuJoCo robotics stack for the UR10e chess arm. Runs inside Docker (ROS Noetic). Vision and the game engine run separately on the host via `Backend/main.py`; IPC is through `Backend/shared/queue/*.json`.

## Quickstart

All interaction goes through `run.sh` from this directory:

```bash
./run.sh <mode>
```

| Mode | What it does |
|------|--------------|
| `real` | Full bringup + launches the robotics pipeline in auto mode |
| `bringup` | Full ROS + UR driver bringup, drops into bash |
| `shell` | Builds the image, sources ROS, drops into bash (no UR driver) |
| `calibrate` | Interactive board calibration (enable Freedrive on tablet first) |
| `kill` | Stops all running Docker containers |

## Running on the robot

```bash
./run.sh real
```

This is equivalent to `bringup` followed by:

```bash
python3 /chess/robotics_pipeline.py --auto --real
```

You can also call that command manually from inside a `bringup` or `shell` session once the UR driver is up and External Control is started on the tablet.

## Development shell

```bash
./run.sh shell   # ROS sourced, roscore running, no UR driver
./run.sh bringup # ROS + UR driver up, drop into bash
```

Inside the container, `src/` is mounted as a live-editable directory `/chess/`
