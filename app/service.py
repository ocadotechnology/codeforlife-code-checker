import typing as t
import json
import re

import pytest

from codeforlife.service.interfaces.kurono_badges import RequestBody, ResponseBody
from codeforlife.kurono import WorldMapCreator, create_avatar_state

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


def run(request: RequestBody):
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
