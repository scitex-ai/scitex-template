"""Optional transport and legacy launchers preserve their actual stream contracts."""

import json
import os
import subprocess
import sys

import pytest

LAUNCHERS = [
    "clone_pip_project",
    "clone_research_minimal",
    "clone_writer_directory",
    "clone_research",
    "clone_singularity",
    "clone_app",
    "clone_module",
    "clone_scitex_minimal",
]


def run(code):
    return subprocess.run(
        [sys.executable, "-c", code],
        env=os.environ.copy(),
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )


@pytest.mark.parametrize("module", LAUNCHERS)
def test_missing_legacy_argument_is_one_stderr_failure_record(module):
    result = run(
        "import importlib; "
        f"importlib.import_module('scitex_template._project.{module}').main([])"
    )
    assert result.returncode == 1
    assert result.stdout == ""
    lines = result.stderr.splitlines()
    assert lines[0].startswith("FAIL: Usage:")
    assert sum(line.startswith("FAIL: ") for line in lines) == 1
    assert all(not line or line.startswith("FAIL| ") for line in lines[1:])


def test_import_does_not_modify_the_stdlib_logger_class():
    result = run(
        "import logging,json\n"
        "before={key:hasattr(logging.Logger,key) for key in ('success','fail')}\n"
        "import scitex_template._utils._logging_helpers\n"
        "after={key:hasattr(logging.Logger,key) for key in ('success','fail')}\n"
        "print(json.dumps({'before':before,'after':after}))\n"
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["before"] == payload["after"]


def test_schemas_import_without_optional_mcp_and_fail_only_when_requested():
    result = run(
        "import sys,json\n"
        "sys.modules['mcp']=None\n"
        "import scitex_template\n"
        "from scitex_template._mcp import tool_schemas\n"
        "assert tool_schemas.types is None\n"
        "try: tool_schemas.get_tool_schemas()\n"
        "except ImportError as error:\n"
        "    assert 'scitex-template[mcp]' in str(error)\n"
        "else: raise AssertionError('optional transport must refuse execution')\n"
        "print(json.dumps({'core_import':True,'transport_refused':True}))\n"
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"core_import": True, "transport_refused": True}
    assert result.stderr == ""


def test_missing_mcp_server_dependency_never_writes_protocol_stdout():
    result = run(
        "import sys,warnings\n"
        "sys.modules['mcp']=None\n"
        "warnings.filterwarnings('ignore', category=DeprecationWarning)\n"
        "from scitex_template.mcp_server import main\n"
        "main()\n"
    )
    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr.startswith("FAIL: ")
    assert "Install: pip install scitex-template[mcp]" in result.stderr


def test_missing_mcp_cli_tool_request_is_a_nonzero_diagnostic():
    result = run(
        "import sys\n"
        "sys.modules['mcp']=None\n"
        "from scitex_template.cli import main\n"
        "main(['mcp','list-tools','--json'])\n"
    )
    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr.startswith("FAIL: ")
    assert "scitex-template[mcp]" in result.stderr


def test_installed_mcp_schemas_and_wrapped_results_remain_json():
    result = run(
        "import asyncio,json,warnings\n"
        "warnings.filterwarnings('ignore',category=DeprecationWarning)\n"
        "from scitex_template._mcp.tool_schemas import get_tool_schemas\n"
        "from scitex_template.mcp_server import TemplateServer\n"
        "schemas=get_tool_schemas()\n"
        "assert schemas and all(s.inputSchema['type']=='object' for s in schemas)\n"
        "server=TemplateServer.__new__(TemplateServer)\n"
        "async def success(): return {'success':True,'value':'synthetic'}\n"
        "async def failure(): raise ValueError('synthetic refusal')\n"
        "async def exercise():\n"
        "    a=await server._wrap_result(success())\n"
        "    b=await server._wrap_result(failure())\n"
        "    return [json.loads(a[0].text),json.loads(b[0].text)]\n"
        "print(json.dumps(asyncio.run(exercise())))\n"
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [
        {"success": True, "value": "synthetic"},
        {"success": False, "error": "synthetic refusal"},
    ]
    assert result.stderr == ""
