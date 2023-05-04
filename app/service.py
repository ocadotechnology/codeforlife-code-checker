import typing as t
from inspect import signature
import json
import re

import pytest

from codeforlife.service.interfaces.kurono_badges import RequestBody, ResponseBody
from codeforlife.kurono import (
    WorldMapCreator,
    create_avatar_state,
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


class PytestPlugin:
    def __init__(self, request: RequestBody):
        self.request = request
        self.response: ResponseBody = None

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

        self.response = ResponseBody(
            passed=summarize_reports("passed"),
            failed=summarize_reports("failed"),
            xfailed=summarize_reports("xfailed"),
            skipped=summarize_reports("skipped"),
        )

    @pytest.fixture
    def source(self):
        return self.request.source

    @pytest.fixture
    def next_turn(self):
        def next_turn(world_state, avatar_state):
            self.request.source._locals["world_state"] = world_state
            self.request.source._locals["avatar_state"] = avatar_state
            return eval(
                "next_turn(world_state, avatar_state)",
                self.request.source._globals,
                self.request.source._locals,
            )

        return next_turn

    @pytest.fixture
    def world_state(self):
        # TODO: refactor
        game_state = json.loads(self.request.game_state.json())
        return WorldMapCreator.generate_world_map_from_game_state(game_state)

    @pytest.fixture
    def avatar_state(self):
        # TODO: refactor
        player = next(
            (
                player
                for player in self.request.game_state.players
                if player.id == self.request.current_avatar_id
            )
        )
        return create_avatar_state(json.loads(player.json()))


def execute(source: RequestBody.Source):
    source._globals.update(
        {
            "direction": direction,
            "location": location,
            "MoveAction": MoveAction,
            "PickupAction": PickupAction,
            "WaitAction": WaitAction,
            "MoveTowardsAction": MoveTowardsAction,
            "DropAction": DropAction,
        }
    )
    exec(source.code, source._globals, source._locals)
    source._globals.update(source._locals)
    source._locals.clear()

    next_turn = source._globals.get("next_turn")
    if not next_turn:
        raise ValueError("next_turn is not defined")
    if not callable(next_turn):
        raise ValueError("next_turn is not a callable")

    next_turn_parameters = signature(next_turn).parameters
    if len(next_turn_parameters) != 2:
        raise ValueError("next_turn expected 2 parameters")
    if list(next_turn_parameters.keys()) != ["world_state", "avatar_state"]:
        raise ValueError("next_turn has the wrong named parameters")


def run(**request_json):
    request = RequestBody(**request_json, execute=execute)

    tests_selection = [f"worksheets/test_worksheet_{request.game_state.worksheetID}.py"]
    if request.task_id:
        tests_selection.append(f"test_task_{request.task_id}")
    plugin = PytestPlugin(request)
    pytest.main(
        args=[
            "-c",
            "pytest.ini",
            "::".join(tests_selection),
        ],
        plugins=[plugin],
    )
    return plugin.response
