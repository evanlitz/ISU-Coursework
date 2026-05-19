FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=noetic

# ── Base tools ────────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    curl wget git \
    build-essential cmake pkg-config \
    lsb-release gnupg2 ca-certificates \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# ── ROS Noetic ────────────────────────────────────────────────────────────────
RUN echo "deb http://packages.ros.org/ros/ubuntu focal main" \
      > /etc/apt/sources.list.d/ros1-latest.list \
 && curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc \
      | apt-key add -

RUN apt-get update && apt-get install -y \
    ros-noetic-ros-base \
    ros-noetic-ros-controllers \
    ros-noetic-ur-msgs \
    ros-noetic-cartesian-interface \
    ros-noetic-cartesian-control-msgs \
    ros-noetic-industrial-robot-status-interface \
    ros-noetic-scaled-joint-trajectory-controller \
    ros-noetic-speed-scaling-interface \
    ros-noetic-speed-scaling-state-controller \
    ros-noetic-ruckig \
    ros-noetic-eigenpy \
    ros-noetic-pass-through-controllers \
    ros-noetic-tf-conversions \
    ros-noetic-kdl-parser \
    ros-noetic-xacro \
    python3-catkin-tools \
    python3-rosdep \
    python3-rosinstall \
    python3-vcstool \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# ── System deps for catkin / UR driver ───────────────────────────────────────
RUN apt-get update && apt-get install -y \
    libyaml-cpp-dev \
    libeigen3-dev \
    libboost-all-dev \
    libpoco-dev \
    liblog4cxx-dev \
    libtinyxml-dev \
    libtinyxml2-dev \
    liburdfdom-dev \
    liborocos-kdl-dev \
    && rm -rf /var/lib/apt/lists/*

# ── Miniforge (Python 3.10 — required by lerobot) ────────────────────────────
RUN curl -fsSL https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh \
      -o /tmp/miniforge.sh \
 && bash /tmp/miniforge.sh -b -p /opt/conda \
 && rm /tmp/miniforge.sh \
 && /opt/conda/bin/conda install -y python=3.10 \
 && /opt/conda/bin/conda clean -afy

ENV PATH=/opt/conda/bin:$PATH
ENV MUJOCO_GL=disabled

# ── Python packages ───────────────────────────────────────────────────────────
# Note: lerobot[feetech] pulls in PyTorch as a transitive dep.
# Replace with a direct STS3215 serial driver to get a truly slim image.
RUN pip install \
    numpy scipy \
    pyserial \
    mujoco \
    matplotlib \
    rospkg catkin_pkg defusedxml

# ── yaml-cpp 0.7.0 (ur_robot_driver master requires >= 0.7, focal ships 0.6) ──
RUN git clone https://github.com/jbeder/yaml-cpp.git --branch yaml-cpp-0.7.0 --depth 1 /tmp/yaml-cpp \
 && cmake -S /tmp/yaml-cpp -B /tmp/yaml-cpp/build \
      -DCMAKE_BUILD_TYPE=Release \
      -DYAML_BUILD_SHARED_LIBS=ON \
      -DCMAKE_INSTALL_PREFIX=/usr \
      -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
 && cmake --build /tmp/yaml-cpp/build -j$(nproc) \
 && cmake --install /tmp/yaml-cpp/build \
 && rm -rf /tmp/yaml-cpp

# ── catkin workspace ──────────────────────────────────────────────────────────
WORKDIR /catkin_ws
COPY docker/catkin_ws/repos.yaml ./repos.yaml

RUN /bin/bash -c "\
    source /opt/ros/noetic/setup.bash && \
    mkdir -p src && \
    vcs import src < repos.yaml && \
    rosdep init && rosdep update && \
    apt-get update && \
    rosdep install --from-paths src --ignore-src -r -y && \
    pip install 'empy==3.3.4' catkin-pkg && \
    catkin build ur_robot_driver --cmake-args -DCMAKE_POLICY_VERSION_MINIMUM=3.5"

# ── Robotics source (volume-mounted in dev; baked in for standalone use) ─────
COPY src/ /chess/
RUN mkdir -p /shared/queue

# ── Entrypoint ────────────────────────────────────────────────────────────────
RUN printf '#!/bin/bash\nset -e\nsource "/opt/ros/$ROS_DISTRO/setup.bash"\n[ -f /catkin_ws/devel/setup.bash ] && source /catkin_ws/devel/setup.bash\n# Ensure shared volume is writable by the host user\nchmod -R a+rwX /shared 2>/dev/null || true\numask 000\nexec "$@"\n' \
    > /ros_entrypoint.sh && chmod +x /ros_entrypoint.sh

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["/bin/bash"]
