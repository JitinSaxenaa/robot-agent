from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Waypoint:
    x: float
    y: float
    yaw: float = 0.0


@dataclass
class Mission:

    mission_type: str

    waypoints: List[Waypoint]

    loops: int = 1

    speed: float = 0.3

    target: Optional[str] = None