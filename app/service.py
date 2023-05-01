import typing as t
from inspect import signature
import json
import re

from pydantic import BaseModel, Field, validator, PrivateAttr
import pytest

from codeforlife.kurono import (
    WorldMapCreator,
    create_avatar_state,
    schema,
    direction,
    location,
    MoveAction,
    PickupAction,
    WaitAction,
    MoveTowardsAction,
    DropAction,
)

if t.TYPE_CHECKING:
    from _pytest.terminal import TerminalReporter


class Source(BaseModel):
    code: str = Field()
    _globals: t.Dict[str, t.Any] = PrivateAttr(
        default_factory=lambda: {
            "direction": direction,
            "location": location,
            "MoveAction": MoveAction,
            "PickupAction": PickupAction,
            "WaitAction": WaitAction,
            "MoveTowardsAction": MoveTowardsAction,
            "DropAction": DropAction,
        }
    )
    _locals: t.Dict[str, t.Any] = PrivateAttr(default_factory=dict)


class Data(BaseModel):
    source: Source = Field()
    current_avatar_id: int = Field()
    task_id: t.Optional[int] = Field(ge=1)
    game_state: schema.GameState = Field()

    @validator("source")
    def defines_next_turn(cls, source: Source):
        exec(source.code, source._globals, source._locals)
        for key in [key for key in source._locals.keys() if key != "next_turn"]:
            source._globals[key] = source._locals.pop(key)

        next_turn = source._locals.get("next_turn")
        if not next_turn:
            raise ValueError("next_turn is not defined")
        if not callable(next_turn):
            raise ValueError("next_turn is not a callable")

        next_turn_parameters = signature(next_turn).parameters
        if len(next_turn_parameters) != 2:
            raise ValueError("next_turn expected 2 parameters")
        if list(next_turn_parameters.keys()) != ["world_state", "avatar_state"]:
            raise ValueError("next_turn has the wrong named parameters")

        return source


class PytestPlugin:
    class ReportSummary(BaseModel):
        class Report(BaseModel):
            task_id: int = Field(ge=1)

        passed: t.List[Report] = Field()
        failed: t.List[Report] = Field()
        xfailed: t.List[Report] = Field()
        skipped: t.List[Report] = Field()

    def __init__(self, data: Data):
        self.data = data
        self.report_summary: PytestPlugin.ReportSummary = None

    def pytest_terminal_summary(self, terminalreporter: "TerminalReporter"):
        def summarize_reports(stats_key: str):
            reports: t.List[pytest.TestReport] = []
            return [
                {
                    "task_id": int(
                        re.match(r"test_task_([0-9]+)", report.head_line).group(1)
                    ),
                }
                for report in terminalreporter.stats.get(stats_key, reports)
            ]

        self.report_summary = self.ReportSummary(
            passed=summarize_reports("passed"),
            failed=summarize_reports("failed"),
            xfailed=summarize_reports("xfailed"),
            skipped=summarize_reports("skipped"),
        )

    @pytest.fixture
    def source(self):
        return self.data.source

    @pytest.fixture
    def next_turn(self):
        def next_turn(world_state, avatar_state):
            self.data.source._locals["world_state"] = world_state
            self.data.source._locals["avatar_state"] = avatar_state
            return eval(
                "next_turn(world_state, avatar_state)",
                self.data.source._globals,
                self.data.source._locals,
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


def run(data: Data):
    tests_selection = [f"worksheets/test_worksheet_{data.game_state.worksheetID}.py"]
    if data.task_id:
        tests_selection.append(f"test_task_{data.task_id}")
    plugin = PytestPlugin(data)
    pytest.main(
        args=[
            "-c",
            "pytest.ini",
            "::".join(tests_selection),
        ],
        plugins=[plugin],
    )
    return plugin.report_summary
