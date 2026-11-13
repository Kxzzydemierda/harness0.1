from __future__ import annotations

from harness.models import AgentResult, Task, ToolResult, VerificationResult
from harness.tools import ToolEngine


class VerificationEngine:
    def __init__(self, tools: ToolEngine):
        self.tools = tools

    def verify(self, task: Task, agent_result: AgentResult, tool_results: list[ToolResult]) -> VerificationResult:
        checks: list[dict] = []
        evidence: list[str] = []
        if not tool_results or any(not result.ok for result in tool_results):
            errors = [result.error for result in tool_results if result.error]
            return VerificationResult(
                passed=False,
                checks=[{"criterion": "La ejecución de herramientas terminó sin errores.", "status": "No cumple", "detail": errors}],
                evidence=[],
            )
        read_result = next(
            (
                item for item in tool_results
                if item.ok
                and item.data.get("path") == agent_result.expected_path
                and "content" in item.data
            ),
            None,
        )
        if read_result is None:
            read_result = self.tools.execute("read_file", {"path": agent_result.expected_path}, task)
        if not read_result.ok:
            return VerificationResult(
                passed=False,
                checks=[{"criterion": "El archivo creado puede leerse para verificarlo.", "status": "No verificable", "detail": read_result.error}],
                evidence=[],
            )
        actual = read_result.data["content"]
        exists = True
        exact = actual == agent_result.expected_content
        evidence.append(f"Lectura real de {agent_result.expected_path}: {len(actual.encode('utf-8'))} bytes.")
        criteria = [criterion.strip().casefold().rstrip(".") for criterion in task.acceptance_criteria]
        exists_aliases = {"el archivo existe", "el archivo solicitado existe", "file exists"}
        content_aliases = {
            "el contenido coincide con el contenido esperado",
            "el contenido es el esperado",
            "content matches expected",
        }
        combined_aliases = {"el archivo existe y contiene el contenido esperado"}
        if not any(item in exists_aliases or item in combined_aliases for item in criteria):
            checks.append({"criterion": "El archivo solicitado existe.", "status": "Cumple" if exists else "No cumple"})
        if not any(item in content_aliases or item in combined_aliases for item in criteria):
            checks.append({"criterion": "El contenido coincide con el contenido esperado.", "status": "Cumple" if exact else "No cumple"})
        if task.acceptance_criteria:
            for criterion in task.acceptance_criteria:
                normalized = criterion.strip().casefold().rstrip(".")
                if normalized in exists_aliases:
                    matched = exists
                elif normalized in content_aliases:
                    matched = exact
                elif normalized in combined_aliases:
                    matched = exists and exact
                else:
                    matched = False
                checks.append(
                    {
                        "criterion": criterion,
                        "status": "Cumple" if matched else "No verificable",
                        "detail": "Comprobación local basada en existencia y comparación exacta." if matched else "El MockProvider no puede evaluar este criterio de forma objetiva.",
                    }
                )
        passed = all(item["status"] == "Cumple" for item in checks)
        return VerificationResult(passed=passed, checks=checks, evidence=evidence)
