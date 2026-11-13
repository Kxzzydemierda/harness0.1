from __future__ import annotations

import re
from abc import ABC, abstractmethod

from harness.models import Analysis, ExecutionPlan, PlanStep, Task, ToolCall


class ModelProvider(ABC):
    """Contrato para proveedores; no presume conexión a un modelo externo."""

    @abstractmethod
    def analyze(self, task: Task) -> Analysis:
        raise NotImplementedError

    @abstractmethod
    def plan(self, task: Task, analysis: Analysis) -> ExecutionPlan:
        raise NotImplementedError

    @abstractmethod
    def actions(self, task: Task, plan: ExecutionPlan) -> list[ToolCall]:
        raise NotImplementedError


class MockProvider(ModelProvider):
    """Proveedor determinista limitado a crear un archivo de texto local."""

    _file_pattern = re.compile(r"(?<![\w.-])([\w.-]+\.(?:txt|md|csv))(?!\w)", re.IGNORECASE)

    def analyze(self, task: Task) -> Analysis:
        text = f"{task.title} {task.description}".lower()
        is_create = any(term in text for term in ("crear", "create", "escribir", "write"))
        has_file = any(term in text for term in ("archivo", "file", ".txt", ".md", ".csv"))
        match = self._file_pattern.search(task.description)
        supported = is_create and has_file and match is not None
        notes = ["MockProvider: análisis determinista; no se consultó un modelo externo."]
        if not supported:
            notes.append("La tarea está fuera de la única capacidad implementada: crear un archivo .txt, .md o .csv.")
        return Analysis(
            objective=f"Crear {match.group(1)} dentro del directorio de trabajo autorizado." if match else task.description,
            supported=supported,
            notes=notes,
        )

    def plan(self, task: Task, analysis: Analysis) -> ExecutionPlan:
        if not analysis.supported:
            return ExecutionPlan(objective=analysis.objective, steps=[])
        filename = self._file_pattern.search(task.description).group(1)
        return ExecutionPlan(
            objective=analysis.objective,
            steps=[
                PlanStep(
                    name="crear_archivo",
                    purpose="Producir el artefacto solicitado dentro del workspace autorizado.",
                    tool="create_file",
                    inputs={"path": filename, "content": self._report_content(filename)},
                    expected_result=f"Archivo creado: {filename}",
                ),
                PlanStep(
                    name="verificar_archivo",
                    purpose="Leer el archivo creado y contrastar su contenido con lo esperado.",
                    tool="read_file",
                    inputs={"path": filename},
                    expected_result="El archivo existe y su contenido coincide exactamente.",
                ),
            ],
        )

    def actions(self, task: Task, plan: ExecutionPlan) -> list[ToolCall]:
        return [
            ToolCall(tool=step.tool, inputs=step.inputs, purpose=step.purpose)
            for step in plan.steps
        ]

    @staticmethod
    def _report_content(filename: str) -> str:
        if "informe" in filename.lower():
            return (
                "Estado de HARNESS0.1\n"
                "HARNESS0.1 cuenta con un núcleo MVP local en Python para recibir encargos, "
                "planificar una tarea acotada, ejecutar herramientas locales autorizadas, "
                "verificar resultados y conservar el historial en SQLite.\n"
                "El flujo inicial utiliza MockProvider; no hay un modelo externo conectado. "
                "La orquestación avanzada, agentes múltiples e integraciones empresariales "
                "siguen siendo trabajo futuro.\n"
            )
        return f"Archivo creado por HARNESS0.1 para la tarea: {filename}.\n"
