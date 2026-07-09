from .schema import Mission


MAX_SPEED = 1.0


def validate_mission(mission: Mission):

    if mission.mission_type == "":
        return False

    if mission.speed <= 0:
        return False

    if mission.speed > MAX_SPEED:
        return False

    if mission.loops < 1:
        return False

    if len(mission.waypoints) == 0:
        return False

    return True