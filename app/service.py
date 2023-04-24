import json

from pydantic import BaseModel, Field, Json
import pytest


class Error(Exception):
    pass


class TestResultsCollector:
    def __init__(self):
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


class Data(BaseModel):
    worksheet_id: int = Field(ge=1, le=2)
    source: str = Field()
    world_state: Json = Field()
    avatar_state: Json = Field()

    # TODO: add validate that source contains "def next_turn(world_state, avatar_state):"


def run(data: Data):
    collector = TestResultsCollector()
    exit_code = pytest.main(
        args=[
            "-c",
            "pytest.ini",
            "--source",
            data.source,
            "--world_state",
            json.dumps(data.world_state),
            "--avatar_state",
            json.dumps(data.avatar_state),
            f"test_worksheet_{data.worksheet_id}.py",
        ],
        plugins=[collector],
    )
    if exit_code != 0:
        raise Error("Tests exited with a non-zero exit status.")
    return collector.json()
