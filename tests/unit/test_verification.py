from pathlib import Path

from harness.app import build_app
from harness.models import TaskStatus


def test_runtime_creates_verifies_and_delivers_real_file(tmp_path: Path) -> None:
    tasks, orchestrator, _ = build_app(tmp_path / "db.sqlite3", tmp_path / "workspace", tmp_path / "entregas")
    task = tasks.create(
        "Crear informe",
        "Crear el archivo informe.txt",
        permissions=["local.create", "local.read"],
        workspace=str(tmp_path / "workspace"),
    )
    finished = orchestrator.run(task.id)
    assert finished.status is TaskStatus.COMPLETED
    assert (tmp_path / "workspace" / "informe.txt").is_file()
    assert (tmp_path / "entregas" / f"{task.id.lower()}-entrega.md").is_file()
