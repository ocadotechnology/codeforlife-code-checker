from app.service import run


def test_task_1():
    task_id = 1
    response = run(
        task_id=task_id,
        source={
            "code": """
import random

def get_random_dir():
    return random.choice(direction.ALL_DIRECTIONS)

def next_turn(world_state, avatar_state):
    while True:
        random_dir = get_random_dir()
        if world_state.can_move_to(avatar_state.location + random_dir):
            return MoveAction(random_dir)
"""
        },
        current_avatar_id=1,
        game_state={
            "era": "future",
            "worksheetID": 2,
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
    assert any(report.task_id == task_id for report in response.passed)


def test_task_2():
    task_id = 2
    response = run(
        task_id=task_id,
        source={
            "code": """
import random

def next_turn(world_state, avatar_state):
    if world_state.cells[avatar_state.location].has_artefact():
        return PickupAction()
"""
        },
        current_avatar_id=1,
        game_state={
            "era": "future",
            "worksheetID": 2,
            "southWestCorner": {"x": -15, "y": -15},
            "northEastCorner": {"x": 15, "y": 15},
            "players": [
                {
                    "location": {"x": 0, "y": 0},
                    "id": 1,
                    "orientation": "north",
                },
            ],
            "interactables": [
                {
                    "location": {"x": 0, "y": 0},
                    "type": "key",
                },
            ],
            "obstacles": [],
            "turnCount": 1,
        },
    )
    assert any(report.task_id == task_id for report in response.passed)
