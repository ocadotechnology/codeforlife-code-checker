from pytest import Parser, fixture, FixtureRequest
import json


def pytest_addoption(parser: Parser):
    parser.addoption("--source", action="store")
    parser.addoption("--world_state", action="store")
    parser.addoption("--avatar_state", action="store")


@fixture
def next_turn(request: FixtureRequest):
    source = request.config.getoption("--source")

    def next_turn(world_state, avatar_state):
        lcls = {
            "world_state": world_state,
            "avatar_state": avatar_state,
        }
        exec(f"{source}\n__return__ = next_turn(world_state, avatar_state)", {}, lcls)
        return lcls["__return__"]

    return next_turn


@fixture
def world_state(request: FixtureRequest):
    world_state = request.config.getoption("--world_state")
    return json.loads(world_state)


@fixture
def avatar_state(request: FixtureRequest):
    avatar_state = request.config.getoption("--avatar_state")
    return json.loads(avatar_state)
