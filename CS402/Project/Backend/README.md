# Backend

Full pipeline for the chess robot: vision, game engine, and robot arm. Tested on **Ubuntu 24.04** with the latest `docker.io` from apt.

## Startup sequence:

Start each component in a separate terminal in order.

---

### 1. Vision

```bash
python vision_module/run.py --live --camera 0
```

Adjust `--camera` to whichever index your board camera is on. This can be left running continously across runs, the game engine passively reads from it.

---

### 2. Robot arm (planner)

In a second terminal, bring up the ROS stack:

```bash
# Option A: full auto (bringup + pipeline, ready to execute moves):
planner/run.sh real

# Option B: manual (useful for debugging):
planner/run.sh bringup   # ROS + UR driver up, drops into bash
# or
planner/run.sh shell     # ROS sourced, no UR driver, drops into bash

# Then inside the container, start the pipeline yourself:
python3 /chess/robotics_pipeline.py --auto --real
```

Start **External Control** on the tablet after the UR driver is up.

---

### 3. Game engine

Once vision is running and the robot is ready:

```bash
python game_engine/main.py --robot_color {black,white} --to_move {black,white}
```

The game engine will wait for input when it's ready to proceed.

## Directory layout

```
Backend/
  vision_module/   board and piece detection
  game_engine/     chess logic and move arbitration
  planner/         ROS + MuJoCo robot stack (runs in Docker)
  shared/          IPC queue files between components
  preflight.py     environment / connection checks
```

## See more:
 - [planner/README.md](planner/README.md) for robotics planner documentation.
 - [vision_module/README.md](vision_module/README.md) for vision documentation.
 - [game_engine/README.md](game_engine/README.md) for game engine documentation.
