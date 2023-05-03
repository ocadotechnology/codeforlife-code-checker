from codeforlife.service.interfaces.kurono_badges import RequestBody

from app.service import run


def test_task_1():
    request = RequestBody(
        task_id=1,
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
    response = run(request)
    assert any(report.task_id == request.task_id for report in response.passed)


def test_task_2():
    request = RequestBody(
        task_id=2,
        source={
            "code": """
import random

def next_turn(world_state, avatar_state):
    new_dir = random.choice(direction.ALL_DIRECTIONS)
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
    response = run(request)
    assert any(report.task_id == request.task_id for report in response.passed)


def test_task_3():
    request = RequestBody(
        task_id=3,
        source={
            "code": """
import random

def next_turn(world_state, avatar_state):
    while True:
        new_dir = random.choice(direction.ALL_DIRECTIONS)
        if world_state.can_move_to(avatar_state.location + new_dir):
            return MoveAction(new_dir)
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
            "obstacles": [
                {
                    "location": {"x": 0, "y": 1},
                    "texture": 1,
                }
            ],
            "turnCount": 1,
        },
    )
    response = run(request)
    assert any(report.task_id == request.task_id for report in response.passed)
