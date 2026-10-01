"""CLI streams retain the shared logging contract and parseable payloads."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from click import unstyle
from click.testing import CliRunner
from scitex_logging import FAIL, INFO, SUCCESS, get_level, set_level

from scitex_template.cli import main


def seed_registry(cache, resource_root):
    """Installed wheels consume a separately populated template registry."""
    cache = Path(cache)
    assert cache.resolve().is_relative_to(Path(resource_root).resolve())
    source = Path(
        os.environ.get(
            "SCITEX_TEMPLATE_TEST_REGISTRY",
            str(Path(__file__).resolve().parents[2] / "templates/REGISTRY.yaml"),
        )
    )
    assert source.is_file()
    destination = cache / "templates/REGISTRY.yaml"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


@pytest.fixture(autouse=True)
def logging_threshold():
    from scitex_template import registry

    if registry._editable_checkout_root() is None:
        seed_registry(registry.CACHE_ROOT, os.environ["SCITEX_DIR"])
    previous = get_level()
    set_level(INFO)
    yield
    set_level(previous)


def test_results_use_stdout_once_across_repeated_invocations():
    runner = CliRunner()
    first = runner.invoke(main, ["list-templates"])
    second = runner.invoke(main, ["list-templates"])
    assert first.exit_code == second.exit_code == 0
    assert first.stdout == second.stdout
    assert all(line.startswith("INFO: ") for line in unstyle(first.stdout).splitlines())
    assert (
        sum(
            line.split()[1] == "research" for line in unstyle(first.stdout).splitlines()
        )
        == 1
    )
    assert first.stderr == second.stderr == ""


def test_rejected_input_is_a_failure_on_stderr():
    result = CliRunner().invoke(main, ["show-info", "does-not-exist"])
    assert result.exit_code == 1
    assert result.stdout == ""
    assert unstyle(result.stderr).startswith("FAIL: ")


def test_multiline_diagnostic_remains_one_record():
    result = CliRunner().invoke(main, ["list"])
    assert result.exit_code == 2
    assert result.stdout == ""
    lines = unstyle(result.stderr).splitlines()
    assert lines[0].startswith("ERRO: ")
    assert lines[1].startswith("ERRO| ")


@pytest.mark.parametrize(
    "args",
    [["--json", "list-templates"], ["mcp", "install", "--claude-code"]],
)
def test_machine_output_is_plain_json(args):
    result = CliRunner().invoke(main, args)
    assert result.exit_code == 0
    assert json.loads(result.stdout)
    assert result.stderr == ""


def test_log_threshold_suppresses_status_without_hiding_json(tmp_path):
    env = {
        **os.environ,
        "SCITEX_DIR": str(tmp_path / ".scitex"),
        "SCITEX_LOGGING_LEVEL": "ERROR",
        "SCITEX_LOGGING_FORMAT": "default",
        "SCITEX_LOGGING_FORCE_COLOR": "0",
        "SCITEX_FORCE_COLOR": "0",
    }
    command = [sys.executable, "-m", "scitex_template"]
    registry_context = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import json; from scitex_template import registry; "
                "print(json.dumps({'cache':str(registry.CACHE_ROOT), "
                "'editable':registry._editable_checkout_root() is not None}))"
            ),
        ],
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
        check=False,
    )
    assert registry_context.returncode == 0, registry_context.stderr
    context = json.loads(registry_context.stdout)
    if not context["editable"]:
        seed_registry(context["cache"], env["SCITEX_DIR"])
    human = subprocess.run(
        command + ["list-templates"],
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
        check=False,
    )
    machine = subprocess.run(
        command + ["list-templates", "--json"],
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
        check=False,
    )
    assert human.returncode == machine.returncode == 0
    assert human.stdout == human.stderr == ""
    assert json.loads(machine.stdout)
    assert machine.stderr == ""


def test_grouped_outcomes_keep_success_and_failure_levels(caplog):
    from scitex_template._utils._logging_helpers import log_final, log_group

    with caplog.at_level("INFO"):
        with log_group("Creating research project") as group:
            group.step("Copied sources")
            group.step("Cannot initialize repository", success=False)
        log_final("Creation failed", success=False)
    records = [
        record
        for record in caplog.records
        if record.name == "scitex_template._utils._logging_helpers"
    ]
    assert [record.levelno for record in records[1:]] == [SUCCESS, FAIL, FAIL]


def test_mcp_doctor_failure_has_nonzero_exit(monkeypatch):
    monkeypatch.setitem(sys.modules, "mcp", None)
    result = CliRunner().invoke(main, ["mcp", "doctor"])
    assert result.exit_code == 1
    assert "FAIL: " in result.stderr
    assert "MCP server ready" not in result.stdout


def test_unavailable_mcp_server_preserves_protocol_stdout(monkeypatch, capsys):
    from scitex_template import mcp_server

    monkeypatch.setattr(mcp_server, "MCP_AVAILABLE", False)
    with pytest.raises(SystemExit) as stopped:
        mcp_server.main()
    streams = capsys.readouterr()
    assert stopped.value.code == 1
    assert streams.out == ""
    assert unstyle(streams.err).startswith("FAIL: ")
