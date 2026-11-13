from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from harness.agents import AgentRuntime
from harness.governance import AuthorizationRequired
from harness.memory import MemoryEngine
from harness.models import Task, TaskStatus, jsonable
from harness.tasks import TaskManager
from harness.tools import ToolEngine
from harness.verification import VerificationEngine


class Orchestrator:
    def __init__(
        self,
        tasks: TaskManager,
        runtime: AgentRuntime,
        tools: ToolEngine,
        verification: VerificationEngine,
        memory: MemoryEngine,
        deliveries: str | Path,
    ):
        self.tasks = tasks
        self.runtime = runtime
        self.tools = tools
        self.verification = verification
        self.memory = memory
        self.deliveries = Path(deliveries).resolve()

    def run(self, task_id: str) -> Task:
        task = self.tasks.get(task_id)
        if task.status in {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED}:
            raise ValueError(f"No se puede ejecutar nuevamente una tarea terminal: {task.status.value}")
        execution_id = uuid4().hex
        started = datetime.now(timezone.utc).isoformat()
        self.memory.start_execution(execution_id, task.id, started)
        plan = None
        result = None
        error = None
        tool_results = []
        tool_calls = []
        tools_executed = []
        try:
            self.tasks.transition(task.id, TaskStatus.ANALYZING)
            for dependency_id in task.dependencies:
                try:
                    dependency = self.tasks.get(dependency_id)
                except KeyError:
                    dependency = None
                if dependency is None or dependency.status != TaskStatus.COMPLETED:
                    reason = f"Dependencia no satisfecha: {dependency_id}"
                    self.tasks.transition(task.id, TaskStatus.BLOCKED, {"reason": reason})
                    result = {"error": reason, "verification": None}
                    self._write_delivery(task, TaskStatus.BLOCKED, result, reason)
                    return self._finish(task.id, execution_id, plan, result, reason, started)
            prepared = self.runtime.prepare(task)
            plan = prepared.plan
            tool_calls = prepared.result.tool_calls
            self.memory.record_event(task.id, "ANALYSIS_COMPLETED", jsonable(prepared.analysis))
            if not prepared.analysis.supported:
                reason = "MockProvider no admite esta tarea."
                self.tasks.transition(task.id, TaskStatus.BLOCKED, {"reason": reason})
                result = {"analysis": jsonable(prepared.analysis), "verification": None}
                self._write_delivery(task, TaskStatus.BLOCKED, result, reason)
                return self._finish(task.id, execution_id, plan, result, reason, started)

            self.tasks.transition(task.id, TaskStatus.PLANNING)
            self.memory.record_event(task.id, "PLAN_CREATED", jsonable(plan))
            self.tasks.transition(task.id, TaskStatus.EXECUTING)
            try:
                for call in prepared.result.tool_calls:
                    tool_result = self.tools.execute(call.tool, call.inputs, self.tasks.get(task.id))
                    if not tool_result.ok:
                        raise RuntimeError(tool_result.error or f"Falló herramienta {call.tool}")
                    tool_results.append(tool_result)
                    tools_executed.append(call.tool)
            except AuthorizationRequired as exc:
                self.tasks.transition(task.id, TaskStatus.REQUIRES_APPROVAL, {"permission": exc.permission, "resource": exc.resource})
                result = {
                    "plan": jsonable(plan),
                    "tool_calls": jsonable(tool_calls),
                    "tools_executed": tools_executed,
                    "tools": jsonable(tool_results),
                    "error": str(exc),
                    "verification": None,
                }
                self._write_delivery(task, TaskStatus.REQUIRES_APPROVAL, result, str(exc))
                return self._finish(task.id, execution_id, plan, result, str(exc), started)
            except Exception as exc:
                self.tasks.transition(task.id, TaskStatus.FAILED, {"error": str(exc)})
                result = {
                    "plan": jsonable(plan),
                    "tool_calls": jsonable(tool_calls),
                    "tools_executed": tools_executed,
                    "tools": jsonable(tool_results),
                    "error": str(exc),
                    "verification": None,
                }
                self._write_delivery(task, TaskStatus.FAILED, result, str(exc))
                return self._finish(task.id, execution_id, plan, result, str(exc), started)

            self.tasks.transition(task.id, TaskStatus.VERIFYING)
            checked = self.verification.verify(task, prepared.result, tool_results)
            self.memory.record_event(task.id, "VERIFICATION_COMPLETED", jsonable(checked))
            result = {
                "agent": jsonable(prepared.result),
                "tool_calls": jsonable(tool_calls),
                "tools_executed": tools_executed,
                "tools": jsonable(tool_results),
                "verification": jsonable(checked),
            }
            target_status = TaskStatus.COMPLETED if checked.passed else TaskStatus.FAILED
            self._write_delivery(task, target_status, result, None)
            self.tasks.transition(task.id, target_status, {"verified": checked.passed})
            return self._finish(task.id, execution_id, plan, result, None, started)
        except AuthorizationRequired as exc:
            current = self.tasks.get(task.id)
            if current.status not in {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.REQUIRES_APPROVAL}:
                self.tasks.transition(
                    task.id,
                    TaskStatus.REQUIRES_APPROVAL,
                    {"permission": exc.permission, "resource": exc.resource},
                )
            result = {
                "plan": jsonable(plan),
                "tool_calls": jsonable(tool_calls),
                "tools_executed": tools_executed,
                "tools": jsonable(tool_results),
                "error": str(exc),
                "verification": None,
            }
            try:
                self._write_delivery(task, TaskStatus.REQUIRES_APPROVAL, result, str(exc))
            except Exception as delivery_error:
                self.memory.record_event(task.id, "DELIVERY_FAILED", {"error": str(delivery_error)})
            return self._finish(task.id, execution_id, plan, result, str(exc), started)
        except Exception as exc:
            error = str(exc)
            current = self.tasks.get(task.id)
            if current.status not in {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.BLOCKED, TaskStatus.REQUIRES_APPROVAL}:
                self.tasks.transition(task.id, TaskStatus.FAILED, {"error": error})
            result = {"error": error}
            try:
                self._write_delivery(task, self.tasks.get(task.id).status, result, error)
            except Exception as delivery_error:
                self.memory.record_event(task.id, "DELIVERY_FAILED", {"error": str(delivery_error)})
            return self._finish(task.id, execution_id, plan, result, error, started)

    def _finish(self, task_id: str, execution_id: str, plan, result, error, started: str) -> Task:
        self.memory.finish_execution(
            execution_id,
            plan,
            result,
            error,
            datetime.now(timezone.utc).isoformat(),
        )
        self.memory.record_event(
            task_id,
            "EXECUTION_FINISHED",
            {"execution_id": execution_id, "started_at": started, "error": error},
        )
        return self.tasks.get(task_id)

    def _write_delivery(self, task: Task, status: TaskStatus, result: dict, error: str | None) -> Path:
        self.deliveries.mkdir(parents=True, exist_ok=True)
        base = self.deliveries / f"{task.id.lower()}-entrega"
        checks = (result.get("verification") or {}).get("checks", [])
        classification = {
            TaskStatus.COMPLETED: "EXITOSA",
            TaskStatus.FAILED: "FALLIDA",
            TaskStatus.CANCELLED: "FALLIDA",
            TaskStatus.BLOCKED: "BLOQUEADA",
            TaskStatus.REQUIRES_APPROVAL: "BLOQUEADA",
        }.get(status, "PARCIALMENTE EXITOSA")
        files = list(
            dict.fromkeys(
                str(item.get("data", {}).get("path"))
                for item in result.get("tools", [])
                if item.get("data", {}).get("path")
            )
        )
        tool_names = sorted(set(result.get("tools_executed", [])))
        check_lines = "\n".join(
            f"- [{item.get('status', 'No verificable')}] {item.get('criterion', '')}"
            for item in checks
        ) or "- No se obtuvieron verificaciones."
        evidence = "\n".join(f"- {item}" for item in (result.get("verification") or {}).get("evidence", [])) or "- No disponible."
        validation_lines = [
            f"- Ejecución de herramientas: {'Cumple' if result.get('tools') and all(item.get('ok') for item in result.get('tools', [])) else 'No cumple o no ejecutada'}.",
            f"- Criterios de aceptación: {'Cumplen todos' if (result.get('verification') or {}).get('passed') else 'Hay criterios pendientes o no cumplidos'}.",
        ]
        text = (
            f"# Entrega — {task.title}\n\n"
            f"**Identificador:** {task.id}  \n"
            f"**Estado del encargo:** {status.value}  \n"
            f"**Clasificación de entrega:** {classification}\n\n"
            f"## Objetivo\n\n{task.description}\n\n"
            f"## Resumen de resultados\n\n"
            f"{'La ejecución terminó y el resultado fue verificado.' if status == TaskStatus.COMPLETED else 'La ejecución no se completó; consulte limitaciones y siguiente paso.'}\n\n"
            f"## Archivos creados o modificados\n\n" + ("\n".join(f"- {item}" for item in files) or "- Ninguno.") + "\n\n"
            f"## Herramientas relevantes\n\n" + ("\n".join(f"- {item}" for item in tool_names) or "- Ninguna.") + "\n\n"
            f"## Evidencias\n\n{evidence}\n\n"
            f"## Pruebas y validaciones\n\n" + "\n".join(validation_lines) + "\n\n"
            f"## Criterios de aceptación\n\n{check_lines}\n\n"
            f"## Errores y limitaciones\n\n{error or 'Ningún error registrado.'}\n\n"
            f"## Continuidad\n\n"
            f"{'No se requiere continuación para esta ejecución.' if status == TaskStatus.COMPLETED else 'Revisar el historial de la tarea, resolver el bloqueo o error y revalidar permisos antes de reintentar.'}\n"
        )
        version = 1
        while True:
            suffix = "" if version == 1 else f"-{version:02d}"
            path = base.with_name(f"{base.name}{suffix}.md")
            try:
                with path.open("x", encoding="utf-8", newline="") as stream:
                    stream.write(text)
                break
            except FileExistsError:
                version += 1
        self.memory.record_event(task.id, "DELIVERY_CREATED", {"path": str(path), "classification": classification})
        return path
