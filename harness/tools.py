from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from harness.governance import AuthorizationRequired, PermissionManager
from harness.memory import MemoryEngine
from harness.models import Task, ToolResult


class ToolError(RuntimeError):
    pass


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: dict[str, type]
    permission: str
    handler: Callable[[dict[str, Any]], dict[str, Any]]


class ToolEngine:
    """Registro de herramientas con validación, autorización y límites de ruta."""

    def __init__(self, workspace: str | Path, permission_manager: PermissionManager, memory: MemoryEngine):
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.permissions = permission_manager
        self.memory = memory
        self.registry: dict[str, ToolDefinition] = {}
        self.register(ToolDefinition("system_time", "Consultar hora UTC del sistema.", {}, "local.time", self._time))
        self.register(ToolDefinition("list_files", "Listar elementos dentro del workspace.", {"path": str}, "local.list", self._list))
        self.register(ToolDefinition("read_file", "Leer archivo de texto del workspace.", {"path": str}, "local.read", self._read))
        self.register(ToolDefinition("create_file", "Crear archivo nuevo sin sobrescribir.", {"path": str, "content": str}, "local.create", self._create))

    def register(self, definition: ToolDefinition) -> None:
        if definition.name in self.registry:
            raise ValueError(f"Herramienta duplicada: {definition.name}")
        self.registry[definition.name] = definition

    def execute(self, name: str, inputs: dict[str, Any], task: Task) -> ToolResult:
        definition = self.registry.get(name)
        if definition is None:
            self.memory.record_event(task.id, "TOOL_REJECTED", {"tool": name, "reason": "unknown tool"})
            return ToolResult(ok=False, error=f"Herramienta desconocida: {name}")
        try:
            self._validate(definition, inputs)
            resource = str(inputs.get("path", self.workspace))
            self.permissions.authorize(task, definition.permission, resource)
            data = definition.handler(inputs)
            self.memory.record_event(
                task.id,
                "TOOL_EXECUTED",
                {"tool": name, "permission": definition.permission, "resource": resource, "result": "success"},
            )
            return ToolResult(ok=True, data=data)
        except AuthorizationRequired:
            raise
        except (ValueError, ToolError, OSError) as exc:
            self.memory.record_event(task.id, "TOOL_FAILED", {"tool": name, "error": str(exc)})
            return ToolResult(ok=False, error=str(exc))

    @staticmethod
    def _validate(definition: ToolDefinition, inputs: dict[str, Any]) -> None:
        if not isinstance(inputs, dict):
            raise ValueError("Las entradas de herramienta deben ser un objeto.")
        expected = set(definition.input_schema)
        actual = set(inputs)
        if actual != expected:
            raise ValueError(f"Entradas inválidas para {definition.name}: se esperan {sorted(expected)}.")
        for key, expected_type in definition.input_schema.items():
            if not isinstance(inputs[key], expected_type):
                raise ValueError(f"Entrada {key} debe ser {expected_type.__name__}.")

    def _resolve(self, relative: str) -> Path:
        if not relative or Path(relative).is_absolute():
            raise ToolError("La ruta debe ser relativa al workspace.")
        candidate = (self.workspace / relative).resolve(strict=False)
        try:
            candidate.relative_to(self.workspace)
        except ValueError as exc:
            raise ToolError("La ruta solicitada sale del workspace autorizado.") from exc
        return candidate

    def _time(self, _: dict[str, Any]) -> dict[str, Any]:
        return {"utc": datetime.now(timezone.utc).isoformat()}

    def _list(self, inputs: dict[str, Any]) -> dict[str, Any]:
        directory = self._resolve(inputs["path"])
        if not directory.is_dir():
            raise ToolError("El directorio solicitado no existe.")
        items = []
        with os.scandir(directory) as entries:
            for entry in entries:
                items.append({"name": entry.name, "is_directory": entry.is_dir(follow_symlinks=False)})
        return {"path": str(directory.relative_to(self.workspace)), "items": sorted(items, key=lambda item: item["name"].casefold())}

    def _read(self, inputs: dict[str, Any]) -> dict[str, Any]:
        path = self._resolve(inputs["path"])
        if not path.is_file():
            raise ToolError("El archivo solicitado no existe.")
        if path.stat().st_size > 1_000_000:
            raise ToolError("El archivo supera el límite de lectura de 1 MB.")
        return {"path": str(path.relative_to(self.workspace)), "content": path.read_text(encoding="utf-8")}

    def _create(self, inputs: dict[str, Any]) -> dict[str, Any]:
        path = self._resolve(inputs["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open("x", encoding="utf-8", newline="") as stream:
                stream.write(inputs["content"])
        except FileExistsError as exc:
            raise ToolError("El archivo ya existe; no se sobrescribió.") from exc
        return {"path": str(path.relative_to(self.workspace)), "bytes": path.stat().st_size}
