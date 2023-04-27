from codeforlife.kurono.direction import Direction
from codeforlife.kurono import (
    MoveAction,
)

from service import Source


# function badge1Trigger(result: any): boolean {
#   // Check the code returns a move action other than NORTH
#   return (
#     result.action.action_type === 'move' &&
#     JSON.stringify(result.action.options.direction) !== JSON.stringify({ x: 0, y: 1 })
#   )
# }
def test_task_1(next_turn, world_state, avatar_state):
    result = next_turn(world_state, avatar_state)
    assert type(result) == MoveAction
    assert result.direction != Direction(x=0, y=1)


# function badge2Trigger(result: any, userPythonCode: string): boolean {
#   // Check code contains keywords to move in random directions
#   const substrings = [
#     'import random',
#     'randint(',
#     'direction.NORTH',
#     'direction.EAST',
#     'direction.SOUTH',
#     'direction.WEST',
#     'if ',
#     'elif ',
#     'else:',
#   ]
#   // Check the code contains certain keywords about moving in a random direction
#   const codeContainsKeywords = substrings.every((substring) => userPythonCode.includes(substring))
#   // And check it returns a move action
#   return result.action.action_type === 'move' && codeContainsKeywords
# }s
def test_task_2(next_turn, world_state, avatar_state, source: Source):
    result = next_turn(world_state, avatar_state)
    # TODO: assert result


# function badge3Trigger(result: any, userPythonCode: string): boolean {
#   // Check the code contains certain keywords about moving to a cell
#   const substrings = ['world_state.can_move_to(', 'print(', 'if ']
#   const codeContainsKeywords = substrings.every((substring) => userPythonCode.includes(substring))
#   // And check it returns a move action
#   return result.action.action_type === 'move' && codeContainsKeywords
# }
def test_task_3(next_turn, world_state, avatar_state):
    result = next_turn(world_state, avatar_state)
    # TODO: assert result
