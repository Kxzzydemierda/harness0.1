from __future__ import annotations

from harness.memory import MemoryEngine
from harness.models import Task


class AuthorizationRequired(PermissionError):
    def __init__(self, permission: str, resource: str):
        self.permission = permission
        self.resource = resource
        super().__init__(f"Se requiere autorización explícita: {permission} sobre {resource}")


class PermissionManager:
    """Comprobación inicial por permisos declarados en el encargo."""

    def __init__(self, memory: MemoryEngine):
        self.memory = memory

    def authorize(self, task: Task, permission: str, resource: str) -> None:
        if permission not in task.permissions:
            self.memory.record_event(
                task.id,
                "AUTHORIZATION_REQUESTED",
                {"permission": permission, "resource": resource, "decision": "REQUIRES_APPROVAL"},
            )
            raise AuthorizationRequired(permission, resource)
        self.memory.record_event(
            task.id,
            "AUTHORIZATION_GRANTED",
            {"permission": permission, "resource": resource, "basis": "explicit task permission"},
        )
