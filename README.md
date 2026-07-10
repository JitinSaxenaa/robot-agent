# Robot Agent — Prompt-to-Navigation Pipeline

A working pipeline where a natural-language instruction is turned into a validated mission plan and executed deterministically on a simulated TurtleBot3 via ROS 2 Nav2.

Prompt → LLM (local, via Ollama) → Validated Mission JSON → Deterministic Executor → Nav2 → Gazebo Simulation

The LLM only proposes a mission plan — it never issues motor commands directly. Every plan is checked against a schema and safety bounds before the executor acts on it, and the executor always produces the same robot behavior for the same JSON input.

## Architecture

- **`mission_planner/schema.py`** — `Mission` / `Waypoint` dataclasses defining the plan format
- **`mission_planner/prompt_parser.py`** — calls a local LLM (Ollama, `llama3.1:8b`) and parses its JSON output into a `Mission`
- **`mission_planner/validator.py`** — rejects missions with invalid speed, loop count, or empty waypoints
- **`mission_planner/mission_runner.py`** — orchestrates parse → validate → return
- **`robot_controller/mission_manager.py`** — thin wrapper exposing `get_mission(prompt)` to the executor
- **`robot_controller/executor.py`** — single ROS 2 node; async `NavigateToPose` action client; sequences waypoints one at a time using goal/feedback/result callbacks (no blocking calls, no nested spinning)

## Requirements

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Harmonic
- TurtleBot3 packages (`turtlebot3_gazebo`, `turtlebot3_navigation2`)
- Python 3.12
- [Ollama](https://ollama.com) with the `llama3.1:8b` model pulled

## Setup

```bash
# ROS 2 Jazzy + Gazebo Harmonic + TurtleBot3 packages assumed already installed
# system-wide via apt, per standard ROS 2 Jazzy install instructions.

# Install Ollama and pull the model
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b

# Python dependencies
pip install ollama --break-system-packages

# Build the workspace
cd ros2_ws
colcon build
source install/setup.bash

## Shell setup (one-time, after running install.sh)

Add these to your `~/.bashrc` so every new terminal is ready automatically:

```bash
echo 'source /opt/ros/jazzy/setup.bash' >> ~/.bashrc
echo 'source ~/robot-agent/ros2_ws/install/setup.bash' >> ~/.bashrc
echo 'export TURTLEBOT3_MODEL=burger' >> ~/.bashrc
source ~/.bashrc
```

Adjust the `ros2_ws` path above if you cloned this repo somewhere other than `~/robot-agent`.
```

## A known TurtleBot3 Nav2 quirk (and our fix)

TurtleBot3's shipped `param/burger.yaml` hardcodes `map_server.yaml_filename: "map.yaml"` — a bare relative path with no directory. This silently breaks map loading regardless of what `map:=` argument you pass at launch, because the params file value takes precedence.

**Fix:** `config/burger_fixed.yaml` in this repo is a copy of the stock params file with that one line corrected to an absolute path. All our launch scripts use this file instead of the stock one.

## Running the simulation

Five terminals, run in order. Each script sources the required ROS environment automatically.

```bash
# Terminal 1 — Gazebo simulation
./scripts/launch_gazebo.sh
# wait for the GUI to load with the robot visible

# Terminal 2 — Nav2 stack (map, localization, planning)
./scripts/launch_nav2.sh
# wait ~30-60s for full startup; do not interrupt this terminal

# Terminal 3 — restart the ROS discovery daemon (avoids stale-node caching)
source /opt/ros/jazzy/setup.bash
ros2 daemon stop && ros2 daemon start
ros2 node list   # confirm map_server, amcl, planner_server, bt_navigator, etc. are present

# Terminal 4 — RViz
./scripts/launch_rviz.sh
# in RViz: click "2D Pose Estimate", then click-and-drag on the map
# at the robot's actual position/heading (compare against the Gazebo view)

# back in Terminal 3, confirm navigation is live:
ros2 lifecycle get /bt_navigator
# should print: active [3]
# if it prints inactive/unconfigured, click "Startup" in RViz's
# Navigation 2 panel and re-check

# Terminal 5 — run a mission from a live prompt
./scripts/run_executor.sh "Patrol a small loop with two waypoints, go slow"
```

Watch the Gazebo window (not just RViz) — the robot physically drives to each waypoint. The terminal log shows the mission JSON being executed step by step:

[executor]: Mission received with 2 waypoint(s)
[executor]: Executing waypoint 1/2
[executor]: Goal Accepted
[executor]: ETA: ...
[executor]: Waypoint Reached
[executor]: Executing waypoint 2/2
...
[executor]: Mission Complete

## Design notes

- **LLM is never in the control loop.** `prompt_parser.py` only ever returns a `Mission` object; nothing downstream trusts LLM output without passing `validator.py` first.
- **Executor is deterministic and auditable.** Given the same validated `Mission`, `executor.py` issues the same sequence of `NavigateToPose` goals every time — no LLM calls happen after mission construction.
- **No blocking calls in the executor.** Early iterations used `rclpy.spin_until_future_complete()` nested inside another spun node, which deadlocks. The current implementation uses a single node with async goal/feedback/result callbacks and a deferred-start timer.

## Citations

- [ros2-agent-ws](https://github.com/limshoonkit/ros2-agent-ws) — reference for the local-LLM-via-Ollama + ROS 2 integration pattern
- [ROS 2 Navigation2](https://github.com/ros-navigation/navigation2) — Nav2 stack
- [TurtleBot3 simulations](https://github.com/ROBOTIS-GIT/turtlebot3_simulations) — simulation base and default map/world
- [Ollama](https://github.com/ollama/ollama) — local LLM runtime