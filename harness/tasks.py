from __future__ import annotations

from datetime import datetime, timezone

from harness.memory import MemoryEngine
from harness.models import Task, TaskStatus


TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.PENDING: {TaskStatus.ANALYZING, TaskStatus.CANCELLED},
    TaskStatus.ANALYZING: {TaskStatus.PLANNING, TaskStatus.BLOCKED, TaskStatus.REQUIRES_APPROVAL, TaskStatus.FAILED, TaskStatus.CANCELLED},
    TaskStatus.PLANNING: {TaskStatus.EXECUTING, TaskStatus.BLOCKED, TaskStatus.REQUIRES_APPROVAL, TaskStatus.FAILED, TaskStatus.CANCELLED},
    TaskStatus.EXECUTING: {TaskStatus.VERIFYING, TaskStatus.BLOCKED, TaskStatus.REQUIRES_APPROVAL, TaskStatus.FAILED, TaskStatus.CANCELLED},
    TaskStatus.VERIFYING: {TaskStatus.COMPLETED, TaskStatus.EXECUTING, TaskStatus.BLOCKED, TaskStatus.REQUIRES_APPROVAL, TaskStatus.FAILED, TaskStatus.CANCELLED},
    TaskStatus.BLOCKED: {TaskStatus.ANALYZING, TaskStatus.REQUIRES_APPROVAL, TaskStatus.FAILED, TaskStatus.CANCELLED},
    TaskStatus.REQUIRES_APPROVAL: {TaskStatus.ANALYZING, TaskStatus.EXECUTING, TaskStatus.BLOCKED, TaskStatus.CANCELLED, TaskStatus.FAILED},
    TaskStatus.COMPLETED: set(),
    TaskStatus.FAILED: set(),
    TaskStatus.CANCELLED: set(),
}


class TaskManager:
    def __init__(self, memory: MemoryEngine):
        self.memory = memory

    def create(
        self,
        title: str,
        description: str,
        acceptance_criteria: list[str] | None = None,
        priority: str = "NORMAL",
        dependencies: list[str] | None = None,
        permissions: list[str] | None = None,
        workspace: str = "",
    ) -> Task:
        if not isinstance(title, str) or not isinstance(description, str) or not title.strip() or not description.strip():
            raise ValueError("El título y la descripción son obligatorios.")
        if not isinstance(priority, str) or priority.upper() not in {"LOW", "NORMAL", "HIGH", "CRITICAL"}:
            raise ValueError("Prioridad inválida.")
        if acceptance_criteria is not None and (
            not isinstance(acceptance_criteria, list)
            or not acceptance_criteria
            or any(not isinstance(item, str) or not item.strip() for item in acceptance_criteria)
        ):
            raise ValueError("Los criterios de aceptación deben ser textos no vacíos.")
        if dependencies is not None and not isinstance(dependencies, list):
            raise ValueError("Las dependencias deben ser una lista de identificadores.")
        if permissions is not None and not isinstance(permissions, list):
            raise ValueError("Los permisos deben ser una lista de identificadores.")
        if any(not isinstance(item, str) or not item.strip() for item in (dependencies or [])):
            raise ValueError("Las dependencias deben ser identificadores no vacíos.")
        if any(not isinstance(item, str) or not item.strip() for item in (permissions or [])):
            raise ValueError("Los permisos deben ser identificadores no vacíos.")
        now = datetime.now(timezone.utc).isoformat()
        task = Task(
            id=self.memory.next_task_identifier(datetime.now(timezone.utc).year),
            title=title.strip(),
            description=description.strip(),
            acceptance_criteria=acceptance_criteria if acceptance_criteria is not None else ["El archivo existe y contiene el contenido esperado."],
            priority=priority.upper(),
            dependencies=dependencies or [],
            permissions=sorted(set(permissions or [])),
            workspace=workspace,
            created_at=now,
            updated_at=now,
        )
        self.memory.create_task(task)
        return task

    def get(self, task_id: str) -> Task:
        return self.memory.get_task(task_id)

    def transition(self, task_id: str, new_status: TaskStatus, details: dict | None = None) -> Task:
        task = self.get(task_id)
        if new_status not in TRANSITIONS[task.status]:
            raise ValueError(f"Transición inválida: {task.status.value} -> {new_status.value}")
        previous = task.status
        task.status = new_status
        task.updated_at = datetime.now(timezone.utc).isoformat()
        self.memory.update_task(task, "STATUS_CHANGED", {"from": previous.value, "to": new_status.value, **(details or {})})
        return task

    def list(self) -> list[Task]:
        return self.memory.list_tasks()

    def cancel(self, task_id: str, reason: str = "Cancelada por solicitud explícita.") -> Task:
        return self.transition(task_id, TaskStatus.CANCELLED, {"reason": reason})
