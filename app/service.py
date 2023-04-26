import typing as t
import json

from pydantic import BaseModel, Field, validator
import pytest

# TODO: fix commented out imports
# from codeforlife.kurono.world_map import WorldMapCreator
# from codeforlife.kurono.avatar_state import create_avatar_state
from kurono import GameState


class Source:
    def __init__(self, value: str):
        self.code = value
        self.globals = {}
        self.locals = {}

        exec(value, self.globals, self.locals)


class Data(BaseModel):
    source: str = Field()
    current_avatar_id: int = Field()
    game_state: GameState = Field()

    @validator("source")
    def defines_next_turn(cls, value: str):
        source = Source(value)

        if "next_turn" not in source.locals:
            raise ValueError("next_turn callable not in source")

        # TODO: validate next_turns arguments' name.

        return source


class TestResultsCollector:
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
                    "head_line": report.head_line,
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
        return WorldMapCreator.generate_world_map_from_game_state(
            self.data.game_state.json()
        )

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
        return create_avatar_state(player.json())


class Error(Exception):
    pass


def run(data: Data):
    collector = TestResultsCollector(data)
    exit_code = pytest.main(
        args=[
            "-c",
            "pytest.ini",
            f"test_worksheet_{data.game_state.worksheetID}.py",
        ],
        plugins=[collector],
    )
    if exit_code != 0:
        raise Error("Tests exited with a non-zero exit status.")
    return collector.json()
