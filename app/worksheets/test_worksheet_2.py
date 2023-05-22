from unittest.mock import Mock, patch

from codeforlife.service.interfaces.kurono_badges import RequestBody
from codeforlife.kurono import (
    direction,
    Cell,
    MoveAction,
    PickupAction,
)


def test_task_1(next_turn, world_state, avatar_state, source: RequestBody.Source):
    # TODO: refactor

    import random

    assert source._globals["random"] == random
    # TODO: talk to Rebecca about this approach.
    # get_random_dir = source._globals["get_random_dir"]
    # assert callable(get_random_dir)

    # get_random_dir_mock = Mock(side_effect=get_random_dir)

    # def assert_finds_way_out(out_dir: direction.Direction):
    #     # Get surrounding obstacle locations.
    #     other_directions = [dir for dir in direction.ALL_DIRECTIONS if dir != out_dir]
    #     obstacle_locations = [avatar_state.location + dir for dir in other_directions]

    #     # Set obstacles in world.
    #     world_state_cells = {
    #         location: Cell(
    #             location={"x": location.x, "y": location.y},
    #             obstacle={
    #                 "location": {"x": location.x, "y": location.y},
    #                 "texture": 1,
    #             },
    #         )
    #         for location in obstacle_locations
    #     }
    #     out_location = avatar_state.location + out_dir
    #     world_state_cells[out_location] = Cell(
    #         {"x": out_location.x, "y": out_location.y}
    #     )

    #     # Get action
    #     with patch.dict(source._globals, {"get_random_dir": get_random_dir_mock}):
    #         with patch.dict(world_state.cells, world_state_cells):
    #             action = next_turn(world_state, avatar_state)

    #     get_random_dir_mock.assert_called()
    #     get_random_dir_mock.reset_mock()

    #     assert type(action) == MoveAction
    #     assert action.direction == out_dir

    # assert_finds_way_out(direction.NORTH)
    # assert_finds_way_out(direction.EAST)
    # assert_finds_way_out(direction.SOUTH)
    # assert_finds_way_out(direction.WEST)

    with patch.object(
        world_state,
        "can_move_to",
        side_effect=world_state.can_move_to,
    ) as world_state__can_move_to:
        action = next_turn(world_state, avatar_state)
        world_state__can_move_to.assert_called()

    assert isinstance(action, MoveAction)


def test_task_2(next_turn, world_state, avatar_state):
    cell: Cell = world_state.cells[avatar_state.location]
    location = {
        "x": avatar_state.location.x,
        "y": avatar_state.location.y,
    }

    with patch.dict(
        world_state.cells,
        {
            avatar_state.location: Cell(
                location,
                interactable={"location": location, "type": "key"},
            )
        },
    ):
        action = next_turn(world_state, avatar_state)
        assert isinstance(action, PickupAction)

    with patch.dict(
        world_state.cells,
        {avatar_state.location: Cell(location, interactable=None)},
    ):
        action = next_turn(world_state, avatar_state)
        assert not isinstance(action, PickupAction)
