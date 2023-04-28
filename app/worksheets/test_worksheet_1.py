import typing as t
from unittest.mock import patch

from codeforlife.kurono.direction import Direction
from codeforlife.kurono import (
    MoveAction,
    direction,
)

from ..service import Source


def test_task_1(next_turn, world_state, avatar_state):
    result = next_turn(world_state, avatar_state)
    assert type(result) == MoveAction
    assert result.direction != direction.NORTH


def test_task_2(next_turn, world_state, avatar_state, source: Source):
    import random

    assert source._globals.get("random") == random

    results: t.List[MoveAction] = [
        next_turn(world_state, avatar_state) for _ in range(100)
    ]

    # TODO: assert "direction." was called at least once.

    assert all(type(result) == MoveAction for result in results)
    assert any(result.direction == direction.NORTH for result in results)
    assert any(result.direction == direction.EAST for result in results)
    assert any(result.direction == direction.SOUTH for result in results)
    assert any(result.direction == direction.WEST for result in results)


def test_task_3(next_turn, world_state, avatar_state):
    # TODO: mock call to print()?
    with patch.object(world_state, "can_move_to") as world_state__can_move_to:
        with patch.object(avatar_state, "location") as avatar_state__location:
            result = next_turn(world_state, avatar_state)
            world_state__can_move_to.assert_called_once()
            avatar_state__location.assert_called_once()
    # TODO: assert result
