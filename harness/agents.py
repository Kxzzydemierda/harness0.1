from __future__ import annotations

from dataclasses import dataclass

from harness.models import AgentResult, Analysis, ExecutionPlan, Task
from harness.providers import ModelProvider


@dataclass
class AgentRun:
    analysis: Analysis
    plan: ExecutionPlan
    result: AgentResult


class AgentRuntime:
    """Ejecuta un agente lógico sobre un proveedor y devuelve estructuras tipadas."""

    def __init__(self, provider: ModelProvider):
        self.provider = provider

    def prepare(self, task: Task) -> AgentRun:
        analysis = self.provider.analyze(task)
        plan = self.provider.plan(task, analysis)
        calls = self.provider.actions(task, plan)
        result = AgentResult(
            summary="; ".join(analysis.notes),
            tool_calls=calls,
            expected_path=plan.steps[0].inputs.get("path", "") if plan.steps else "",
            expected_content=plan.steps[0].inputs.get("content", "") if plan.steps else "",
        )
        return AgentRun(analysis=analysis, plan=plan, result=result)
