from mission_planner.prompt_parser import parse_prompt
from mission_planner.validator import validate_mission


def build_mission(prompt: str = "Go to A"):

    mission = parse_prompt(prompt)

    if not validate_mission(mission):
        raise Exception("Invalid mission")

    return mission