from pathlib import Path

import pytest

from harness.memory import MemoryEngine
from harness.models import TaskStatus
from harness.tasks import TaskManager


def make_tasks(tmp_path: Path) -> TaskManager:
    return TaskManager(MemoryEngine(tmp_path / "state.sqlite3"))


def test_task_creation_persists_and_assigns_id(tmp_path: Path) -> None:
    manager = make_tasks(tmp_path)
    task = manager.create("T", "Crear informe.txt")
    assert task.id.startswith("ENC-")
    assert task.status is TaskStatus.PENDING
    assert manager.get(task.id).description == "Crear informe.txt"


def test_invalid_status_transition_is_rejected(tmp_path: Path) -> None:
    manager = make_tasks(tmp_path)
    task = manager.create("T", "Crear informe.txt")
    with pytest.raises(ValueError, match="Transición inválida"):
        manager.transition(task.id, TaskStatus.COMPLETED)


def test_valid_transitions_are_persisted_in_history(tmp_path: Path) -> None:
    manager = make_tasks(tmp_path)
    task = manager.create("T", "Crear informe.txt")
    manager.transition(task.id, TaskStatus.ANALYZING)
    manager.transition(task.id, TaskStatus.PLANNING)
    assert manager.get(task.id).status is TaskStatus.PLANNING
    assert [event["kind"] for event in manager.memory.history(task.id)] == [
        "TASK_CREATED",
        "STATUS_CHANGED",
        "STATUS_CHANGED",
    ]


def test_invalid_priority_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Prioridad inválida"):
        make_tasks(tmp_path).create("T", "Crear informe.txt", priority="URGENT")


def test_task_ids_follow_documented_sequence_and_cancel(tmp_path: Path) -> None:
    manager = make_tasks(tmp_path)
    first = manager.create("T1", "Crear a.txt")
    second = manager.create("T2", "Crear b.txt")
    assert first.id.endswith("-0001")
    assert second.id.endswith("-0002")
    assert manager.cancel(first.id).status is TaskStatus.CANCELLED
