#!/bin/bash
set -e

echo "=== Robot Agent — Install Script ==="
echo "Tested on Ubuntu 24.04.4 LTS (noble) with ROS 2 Jazzy"
echo ""

# --- 1. ROS 2 Jazzy apt repository ---
echo "--- Setting up ROS 2 apt repository ---"
sudo apt update && sudo apt install -y software-properties-common curl
sudo add-apt-repository universe -y

sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

sudo apt update

# --- 2. ROS 2 Jazzy desktop (includes Gazebo Harmonic via ros-gz packages) ---
echo "--- Installing ROS 2 Jazzy desktop + dev tools ---"
sudo apt install -y ros-jazzy-desktop ros-dev-tools

# --- 3. TurtleBot3 packages ---
echo "--- Installing TurtleBot3 packages ---"
sudo apt install -y \
  ros-jazzy-turtlebot3 \
  ros-jazzy-turtlebot3-gazebo \
  ros-jazzy-turtlebot3-navigation2 \
  ros-jazzy-turtlebot3-simulations \
  ros-jazzy-turtlebot3-bringup \
  ros-jazzy-turtlebot3-msgs
  
  echo "--- Installing tf_transformations ---"
sudo apt install -y ros-jazzy-tf-transformations

# --- 4. Ollama (local LLM runtime) ---
echo "--- Installing Ollama ---"
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b

# --- 5. Python dependencies ---
echo "--- Installing Python dependencies ---"
pip install ollama --break-system-packages

# --- 6. Build the workspace ---
echo "--- Building ROS 2 workspace ---"
cd "$(dirname "$0")/ros2_ws"
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash

echo ""
echo "=== Install complete ==="
echo "Add these to your ~/.bashrc so every new terminal is ready automatically:"
echo "  source /opt/ros/jazzy/setup.bash"
echo "  source $(pwd)/install/setup.bash"
echo "  export TURTLEBOT3_MODEL=burger"
echo ""
echo "Then run the simulation — see README.md for the full launch sequence."