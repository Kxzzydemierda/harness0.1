from pathlib import Path

import pytest

from harness.governance import AuthorizationRequired, PermissionManager
from harness.memory import MemoryEngine
from harness.tasks import TaskManager
from harness.tools import ToolEngine


def setup_tools(tmp_path: Path, permissions: list[str]):
    memory = MemoryEngine(tmp_path / "db.sqlite3")
    task = TaskManager(memory).create("T", "crear nota.txt", permissions=permissions)
    workspace = tmp_path / "workspace"
    tools = ToolEngine(workspace, PermissionManager(memory), memory)
    return tools, task, workspace


def test_create_read_and_list_are_real_and_scoped(tmp_path: Path) -> None:
    tools, task, workspace = setup_tools(tmp_path, ["local.create", "local.read", "local.list"])
    created = tools.execute("create_file", {"path": "nested/nota.txt", "content": "contenido"}, task)
    assert created.ok
    assert (workspace / "nested" / "nota.txt").read_text(encoding="utf-8") == "contenido"
    assert tools.execute("read_file", {"path": "nested/nota.txt"}, task).data["content"] == "contenido"
    assert "nota.txt" in [item["name"] for item in tools.execute("list_files", {"path": "nested"}, task).data["items"]]


@pytest.mark.parametrize("path", ["../fuera.txt", "..\\fuera.txt", "C:\\fuera.txt", ""])
def test_paths_cannot_escape_workspace(tmp_path: Path, path: str) -> None:
    tools, task, _ = setup_tools(tmp_path, ["local.create"])
    result = tools.execute("create_file", {"path": path, "content": "x"}, task)
    assert not result.ok


def test_existing_file_is_never_overwritten(tmp_path: Path) -> None:
    tools, task, workspace = setup_tools(tmp_path, ["local.create"])
    (workspace / "keep.txt").write_text("original", encoding="utf-8")
    result = tools.execute("create_file", {"path": "keep.txt", "content": "changed"}, task)
    assert not result.ok
    assert (workspace / "keep.txt").read_text(encoding="utf-8") == "original"


def test_missing_permission_requests_approval_without_action(tmp_path: Path) -> None:
    tools, task, workspace = setup_tools(tmp_path, [])
    with pytest.raises(AuthorizationRequired):
        tools.execute("create_file", {"path": "no.txt", "content": "x"}, task)
    assert not (workspace / "no.txt").exists()
    assert tools.memory.history(task.id)[-1]["kind"] == "AUTHORIZATION_REQUESTED"


def test_tool_input_schema_is_validated(tmp_path: Path) -> None:
    tools, task, _ = setup_tools(tmp_path, ["local.create"])
    result = tools.execute("create_file", {"path": "x.txt", "content": 4}, task)
    assert not result.ok
