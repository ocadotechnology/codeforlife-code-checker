from unittest.mock import Mock, patch

from codeforlife.kurono import (
    direction,
    Cell,
    MoveAction,
    PickupAction,
)

from ..service import Source


def test_task_1(next_turn, world_state, avatar_state, source: Source):
    # TODO: refactor

    import random

    assert source._globals.get("random") == random
    get_random_dir = source._globals["get_random_dir"]
    assert callable(get_random_dir)

    get_random_dir_mock = Mock(side_effect=get_random_dir)

    def assert_finds_way_out(out_dir: direction.Direction):
        # Get surrounding obstacle locations.
        other_directions = [dir for dir in direction.ALL_DIRECTIONS if dir != out_dir]
        obstacle_locations = [avatar_state.location + dir for dir in other_directions]

        # Set obstacles in world.
        world_state_cells = {
            location: Cell(
                location={"x": location.x, "y": location.y},
                obstacle={
                    "location": {"x": location.x, "y": location.y},
                    "texture": 1,
                },
            )
            for location in obstacle_locations
        }
        out_location = avatar_state.location + out_dir
        world_state_cells[out_location] = Cell(
            {"x": out_location.x, "y": out_location.y}
        )

        # Get action
        with patch.dict(source._globals, {"get_random_dir": get_random_dir_mock}):
            with patch.dict(world_state.cells, world_state_cells):
                action = next_turn(world_state, avatar_state)

        get_random_dir_mock.assert_called()
        get_random_dir_mock.reset_mock()

        assert type(action) == MoveAction
        assert action.direction == out_dir

    assert_finds_way_out(direction.NORTH)
    assert_finds_way_out(direction.EAST)
    assert_finds_way_out(direction.SOUTH)
    assert_finds_way_out(direction.WEST)


def test_task_2(next_turn, world_state, avatar_state):
    assert world_state.cells[avatar_state.location].has_artefact()
    action = next_turn(world_state, avatar_state)
    assert type(action) == PickupAction
