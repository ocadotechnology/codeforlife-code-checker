from time import time
import json

from flask import Flask, request, Response, jsonify
from pydantic import BaseModel, Field, ValidationError, Json
from waitress import serve
import pytest

json.detect_encoding
app = Flask(__name__)


class Data(BaseModel):
    worksheet_id: int = Field(ge=1, le=2)
    source: str = Field()
    world_state: Json = Field()
    avatar_state: Json = Field()

    # TODO: add validate that source contains "def next_turn(world_state, avatar_state):"


class TestResultsCollector:
    def __init__(self):
        self.reports = []
        self.collected = 0
        self.exitcode = 0
        self.passed = 0
        self.failed = 0
        self.xfailed = 0
        self.skipped = 0
        self.total_duration = 0

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        if report.when == "call":
            self.reports.append(report)

    def pytest_collection_modifyitems(self, items):
        self.collected = len(items)

    def pytest_terminal_summary(self, terminalreporter, exitstatus):
        print(exitstatus, dir(exitstatus))
        self.exitcode = exitstatus.value
        self.passed = len(terminalreporter.stats.get("passed", []))
        self.failed = len(terminalreporter.stats.get("failed", []))
        self.xfailed = len(terminalreporter.stats.get("xfailed", []))
        self.skipped = len(terminalreporter.stats.get("skipped", []))

        self.total_duration = time() - terminalreporter._sessionstarttime


def run_tests(data: Data):
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
        # plugins=[collector],
    )
    if exit_code != 0:
        return Response("Failed to run tests.", status=500)
    return jsonify()#**collector.reports)


@app.route("/", methods=["POST"])
def run():
    try:
        data = Data(**request.json)
    except ValidationError as error:
        return Response(error.json(), status=400, content_type="application/json")
    return run_tests(data)


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port="8080")
