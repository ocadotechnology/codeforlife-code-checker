from inspect import signature
import json
import re

from pydantic import BaseModel, Field, validator
import pytest

from codeforlife.kurono import WorldMapCreator, create_avatar_state, schema


class Source:
    def __init__(self, value: str):
        self.code = value
        self.globals = {}
        self.locals = {}

        exec(value, self.globals, self.locals)


class Data(BaseModel):
    source: str = Field()
    current_avatar_id: int = Field()
    game_state: schema.GameState = Field()

    @validator("source")
    def defines_next_turn(cls, value: str):
        source = Source(value)

        next_turn = source.locals.get("next_turn")
        if not next_turn:
            raise ValueError("next_turn not defined in source")
        if not callable(next_turn):
            raise ValueError("next_turn is not a callable")

        next_turn_parameters = signature(next_turn).parameters
        if len(next_turn_parameters) != 2:
            raise ValueError("next_turn expected 2 parameters")
        if list(next_turn_parameters.keys()) != ["world_state", "avatar_state"]:
            raise ValueError("next_turn has the wrong named parameters")

        return source


class PytestPlugin:
    def __init__(self, data: Data):
        self.data = data
        self.passed = []
        self.failed = []
        self.xfailed = []
        self.skipped = []

    def pytest_terminal_summary(self, terminalreporter):
        self.passed = terminalreporter.stats.get("passed", [])
        self.failed = terminalreporter.stats.get("failed", [])
        self.xfailed = terminalreporter.stats.get("xfailed", [])
        self.skipped = terminalreporter.stats.get("skipped", [])

    def json(self):
        obj = {}

        def get_reports(name: str):
            obj[name] = [
                {
                    "task_id": int(
                        re.match(r"test_task_([0-9]+)", report.head_line).group(1)
                    ),
                }
                for report in getattr(self, name)
            ]

        get_reports("passed")
        get_reports("failed")
        get_reports("xfailed")
        get_reports("skipped")

        return json.dumps(obj)

    @pytest.fixture
    def next_turn(self):
        def next_turn(world_state, avatar_state):
            self.data.source.locals["world_state"] = world_state
            self.data.source.locals["avatar_state"] = avatar_state
            return eval(
                "next_turn(world_state, avatar_state)",
                self.data.source.globals,
                self.data.source.locals,
            )

        return next_turn

    @pytest.fixture
    def world_state(self):
        # TODO: refactor
        game_state = json.loads(self.data.game_state.json())
        return WorldMapCreator.generate_world_map_from_game_state(game_state)

    @pytest.fixture
    def avatar_state(self):
        # TODO: refactor
        player = next(
            (
                player
                for player in self.data.game_state.players
                if player.id == self.data.current_avatar_id
            )
        )
        return create_avatar_state(json.loads(player.json()))


class Error(Exception):
    pass


def run(data: Data):
    plugin = PytestPlugin(data)
    exit_code = pytest.main(
        args=[
            "-c",
            "pytest.ini",
            f"test_worksheet_{data.game_state.worksheetID}.py",
        ],
        plugins=[plugin],
    )
    if exit_code != 0:
        raise Error("Tests exited with a non-zero exit status.")
    return plugin.json()
