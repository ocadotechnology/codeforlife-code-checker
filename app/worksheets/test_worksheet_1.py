import typing as t
from unittest.mock import patch

from codeforlife.service.interfaces.kurono_badges import RequestBody
from codeforlife.kurono import (
    MoveAction,
    direction,
)


def test_task_1(next_turn, world_state, avatar_state):
    action = next_turn(world_state, avatar_state)
    assert isinstance(action, MoveAction)
    assert action.direction != direction.NORTH


def test_task_2(next_turn, world_state, avatar_state, source: RequestBody.Source):
    import random

    assert source._globals["random"] == random

    actions: t.List[MoveAction] = [
        next_turn(world_state, avatar_state) for _ in range(1000)
    ]

    assert all(isinstance(action, MoveAction) for action in actions)
    assert any(action.direction == direction.NORTH for action in actions)
    assert any(action.direction == direction.EAST for action in actions)
    assert any(action.direction == direction.SOUTH for action in actions)
    assert any(action.direction == direction.WEST for action in actions)


def test_task_3(next_turn, world_state, avatar_state):
    # TODO: make world_state and avatar_state mutable.
    # TODO: patch avatar_state.location as a non-callable mock and assert it's referenced.

    with patch.object(
        world_state,
        "can_move_to",
        side_effect=world_state.can_move_to,
    ) as world_state__can_move_to:
        action = next_turn(world_state, avatar_state)
        world_state__can_move_to.assert_called()

    assert isinstance(action, MoveAction)
