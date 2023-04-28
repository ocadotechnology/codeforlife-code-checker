import json

from codeforlife.kurono.schema import GameState

from app.service import Data, run


def test_run():
    data = Data(
        source={
            "code": """
def next_turn(world_state, avatar_state):
    new_dir = direction.SOUTH
    action = MoveAction(new_dir)
    return action
"""
        },
        current_avatar_id=1,
        game_state={
            "era": "future",
            "worksheetID": 1,
            "southWestCorner": {"x": -15, "y": -15},
            "northEastCorner": {"x": 15, "y": 15},
            "players": [
                {
                    "location": {"x": 0, "y": 0},
                    "id": 1,
                    "orientation": "north",
                },
            ],
            "interactables": [],
            "obstacles": [],
            "turnCount": 1,
        },
    )
    result = json.loads(run(data))
    assert any(passed["task_id"] == 1 for passed in result["passed"])
