from pathlib import Path

from harness.app import build_app
from harness.models import TaskStatus
import pytest


def test_end_to_end_file_creation_verification_and_history(tmp_path: Path) -> None:
    workspace = tmp_path / "authorized-workspace"
    deliveries = tmp_path / "entregas"
    tasks, orchestrator, memory = build_app(tmp_path / "harness.sqlite3", workspace, deliveries)
    task = tasks.create(
        title="Preparar informe de estado",
        description="Crear un archivo llamado informe.txt dentro del directorio de trabajo autorizado, escribir un pequeño informe sobre el estado de HARNESS0.1 y verificar que el archivo existe y contiene el contenido esperado.",
        acceptance_criteria=[
            "El archivo existe.",
            "El contenido coincide con el contenido esperado.",
        ],
        permissions=["local.create", "local.read"],
        workspace=str(workspace),
    )

    finished = orchestrator.run(task.id)

    report = (workspace / "informe.txt").read_text(encoding="utf-8")
    assert finished.status is TaskStatus.COMPLETED
    assert "Estado de HARNESS0.1" in report
    assert "no hay un modelo externo conectado" in report
    assert (deliveries / f"{task.id.lower()}-entrega.md").is_file()
    assert memory.executions(task.id)[0]["error"] is None
    kinds = [event["kind"] for event in memory.history(task.id)]
    assert "PLAN_CREATED" in kinds
    assert "TOOL_EXECUTED" in kinds
    assert "VERIFICATION_COMPLETED" in kinds
    assert "DELIVERY_CREATED" in kinds
    assert memory.get_task(task.id).status is TaskStatus.COMPLETED


def test_missing_permission_blocks_and_records_request(tmp_path: Path) -> None:
    workspace = tmp_path / "authorized-workspace"
    tasks, orchestrator, memory = build_app(tmp_path / "harness.sqlite3", workspace, tmp_path / "entregas")
    task = tasks.create("Preparar informe", "Crear informe.txt", permissions=["local.create"], workspace=str(workspace))

    finished = orchestrator.run(task.id)

    assert finished.status is TaskStatus.REQUIRES_APPROVAL
    assert (workspace / "informe.txt").exists()
    history = memory.history(task.id)
    assert any(event["kind"] == "AUTHORIZATION_REQUESTED" for event in history)
    request = next(event for event in history if event["kind"] == "AUTHORIZATION_REQUESTED")
    assert request["details"]["permission"] == "local.read"
    assert (tmp_path / "entregas" / f"{task.id.lower()}-entrega.md").exists()


def test_unmet_dependency_blocks_before_tool_execution(tmp_path: Path) -> None:
    workspace = tmp_path / "authorized-workspace"
    tasks, orchestrator, memory = build_app(tmp_path / "harness.sqlite3", workspace, tmp_path / "entregas")
    task = tasks.create(
        "Preparar informe",
        "Crear informe.txt",
        dependencies=["ENC-2026-9999"],
        permissions=["local.create", "local.read"],
        workspace=str(workspace),
    )

    finished = orchestrator.run(task.id)

    assert finished.status is TaskStatus.BLOCKED
    assert not (workspace / "informe.txt").exists()
    assert not any(event["kind"] == "TOOL_EXECUTED" for event in memory.history(task.id))


def test_blocked_dependency_can_resume_without_overwriting_delivery(tmp_path: Path) -> None:
    workspace = tmp_path / "authorized-workspace"
    deliveries = tmp_path / "entregas"
    tasks, orchestrator, _ = build_app(tmp_path / "harness.sqlite3", workspace, deliveries)
    dependency = tasks.create("Crear dependencia", "Crear previo.txt", permissions=["local.create", "local.read"], workspace=str(workspace))
    task = tasks.create(
        "Preparar informe",
        "Crear informe.txt",
        dependencies=[dependency.id],
        permissions=["local.create", "local.read"],
        workspace=str(workspace),
    )

    assert orchestrator.run(task.id).status is TaskStatus.BLOCKED
    first_delivery = deliveries / f"{task.id.lower()}-entrega.md"
    first_contents = first_delivery.read_text(encoding="utf-8")
    assert orchestrator.run(dependency.id).status is TaskStatus.COMPLETED
    assert orchestrator.run(task.id).status is TaskStatus.COMPLETED

    second_delivery = deliveries / f"{task.id.lower()}-entrega-02.md"
    assert first_delivery.read_text(encoding="utf-8") == first_contents
    assert second_delivery.is_file()


def test_terminal_task_cannot_be_run_twice(tmp_path: Path) -> None:
    workspace = tmp_path / "authorized-workspace"
    tasks, orchestrator, _ = build_app(tmp_path / "harness.sqlite3", workspace, tmp_path / "entregas")
    task = tasks.create("Crear informe", "Crear informe.txt", permissions=["local.create", "local.read"], workspace=str(workspace))
    assert orchestrator.run(task.id).status is TaskStatus.COMPLETED
    with pytest.raises(ValueError, match="tarea terminal"):
        orchestrator.run(task.id)


def test_unknown_acceptance_criterion_is_not_assumed_satisfied(tmp_path: Path) -> None:
    workspace = tmp_path / "authorized-workspace"
    tasks, orchestrator, memory = build_app(tmp_path / "harness.sqlite3", workspace, tmp_path / "entregas")
    task = tasks.create(
        "Crear informe",
        "Crear informe.txt",
        acceptance_criteria=["El informe incluye una conclusión aprobada por finanzas."],
        permissions=["local.create", "local.read"],
        workspace=str(workspace),
    )

    finished = orchestrator.run(task.id)

    assert finished.status is TaskStatus.FAILED
    execution = memory.executions(task.id)[0]
    check = execution["result"]["verification"]["checks"][-1]
    assert check["status"] == "No verificable"
