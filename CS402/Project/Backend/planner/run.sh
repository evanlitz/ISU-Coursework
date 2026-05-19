#!/usr/bin/env bash
# planner/run.sh — Robot pipeline launcher
#
# Manages the Docker container that runs ROS + UR driver + MuJoCo IK.
# Vision and game engine run separately on the host via Backend/main.py.
# IPC is through Backend/shared/queue/*.json.
#
# Usage: ./run.sh <mode>
#
# Modes:
#   real        Start ROS + UR driver + robotics pipeline (listens for moves)
#   calibrate   Interactive board calibration (enable Freedrive on tablet first)
#   shell       Build, source everything, bring up roscore, drop into bash
#   bringup     Full ROS + UR driver bringup, no pipeline — drop into bash
#   kill        Stop and remove all running Docker containers

set -euo pipefail

PLANNER="$(cd "$(dirname "$0")" && pwd)"   # Backend/planner/
DOCKER="$PLANNER/docker"                   # Backend/planner/docker/

# ── Helpers ───────────────────────────────────────────────────────────────────

_docker_up() {
    echo "[run.sh] Building and starting container..."
    cd "$DOCKER"
    sudo docker compose up --build -d
    echo "[run.sh] Container ready."
}

_ros_exec() {
    # $1 — command to run after ROS + UR driver are up
    sudo docker compose -f "$DOCKER/docker-compose.yml" exec robot bash -c "
        set -e
        source /opt/ros/noetic/setup.bash
        source /catkin_ws/devel/setup.bash

        roscore &
        ROSCORE_PID=\$!

        echo '[run.sh] Waiting for roscore...'
        until (echo > /dev/tcp/localhost/11311) 2>/dev/null; do sleep 1; done
        echo '[run.sh] roscore ready.'

        roslaunch ur_robot_driver ur10e_bringup.launch \
            robot_ip:=\${ROBOT_IP:-192.168.56.100} \

        echo '[run.sh] UR driver up — start External Control on the tablet.'
        $1
    "
}

_ros_shell() {
    # Interactive shell with roscore only — no UR driver.
    sudo docker compose -f "$DOCKER/docker-compose.yml" exec robot bash --login -c "
        set -e

        echo '[run.sh] Sourcing ROS + workspace...'
        source /opt/ros/noetic/setup.bash
        source /catkin_ws/devel/setup.bash

        if ! (echo > /dev/tcp/localhost/11311) 2>/dev/null; then
            echo '[run.sh] Starting roscore...'
            roscore &
            until (echo > /dev/tcp/localhost/11311) 2>/dev/null; do sleep 1; done
            echo '[run.sh] roscore ready.'
        else
            echo '[run.sh] roscore already running.'
        fi

        echo ''
        echo '  ROS_DISTRO : \$ROS_DISTRO'
        echo '  ROS_MASTER  : \$ROS_MASTER_URI'
        echo '  Workspace   : /catkin_ws/devel'
        echo '  Source      : /chess'
        echo ''

        printf 'source /opt/ros/noetic/setup.bash\nsource /catkin_ws/devel/setup.bash\nexport PS1=\"[ros:\\w]\\$ \"\n' > /tmp/ros_rc
        exec bash --rcfile /tmp/ros_rc
    "
}

usage() {
    sed -n '2,15p' "$0" | sed 's/^# \?//'
    exit 1
}

[ $# -lt 1 ] && usage

# ── Modes ─────────────────────────────────────────────────────────────────────

case "$1" in

    real)
        _docker_up
        _ros_exec "python3 /chess/robotics_pipeline.py --auto --real"
        ;;

    calibrate)
        _docker_up
        _ros_exec "python3 /chess/calibrate_board.py"
        ;;

    shell)
        _docker_up
        _ros_shell
        ;;

    bringup)
        _docker_up
        _ros_exec "bash"
        ;;

    kill)
        echo "[run.sh] Stopping all running Docker containers..."
        CONTAINERS=$(sudo docker ps -q)
        if [ -z "$CONTAINERS" ]; then
            echo "[run.sh] No containers running."
        else
            sudo docker stop $CONTAINERS
            echo "[run.sh] All containers stopped."
        fi
        ;;

    -h|--help|help)
        usage
        ;;

    *)
        echo "Unknown mode: '$1'"
        usage
        ;;

esac