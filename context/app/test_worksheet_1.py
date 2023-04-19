def test_task_1(next_turn, world_state, avatar_state):
    assert next_turn(world_state, avatar_state) != "NORTH"
