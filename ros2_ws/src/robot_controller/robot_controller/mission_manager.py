from mission_planner.mission_runner import build_mission


class MissionManager:

    def get_mission(self, prompt: str = "Go to A"):
        return build_mission(prompt)