import json
import ollama

from .schema import Mission, Waypoint

_SYSTEM_PROMPT = """You convert a natural-language robot instruction into STRICT JSON only.
No markdown, no explanation, no code fences. Output must match this shape exactly:

{
  "mission_type": "waypoint_navigation",
  "waypoints": [{"x": <float>, "y": <float>, "yaw": <float>}, ...],
  "loops": <int>,
  "speed": <float>
}

Rules:
- speed must be between 0.05 and 1.0
- loops must be >= 1
- yaw defaults to 0.0 if not specified
- Output ONLY the JSON object, nothing else.
"""


def parse_prompt(prompt: str) -> Mission:
    response = ollama.chat(
        model="llama3.1:8b",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        format="json",
    )

    raw_text = response["message"]["content"].strip()

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM did not return valid JSON: {raw_text}") from e

    waypoints = [
        Waypoint(
            x=float(wp["x"]),
            y=float(wp["y"]),
            yaw=float(wp.get("yaw", 0.0)),
        )
        for wp in data["waypoints"]
    ]

    return Mission(
        mission_type=data.get("mission_type", "waypoint_navigation"),
        waypoints=waypoints,
        loops=int(data.get("loops", 1)),
        speed=float(data.get("speed", 0.3)),
    )