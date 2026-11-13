from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class TaskStatus(StrEnum):
    PENDING = "PENDING"
    ANALYZING = "ANALYZING"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class Task:
    id: str
    title: str
    description: str
    acceptance_criteria: list[str]
    priority: str = "NORMAL"
    dependencies: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    workspace: str = ""
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Analysis:
    objective: str
    supported: bool
    notes: list[str] = field(default_factory=list)


@dataclass
class PlanStep:
    name: str
    purpose: str
    tool: str
    inputs: dict[str, Any]
    expected_result: str


@dataclass
class ExecutionPlan:
    objective: str
    steps: list[PlanStep]


@dataclass
class ToolCall:
    tool: str
    inputs: dict[str, Any]
    purpose: str


@dataclass
class ToolResult:
    ok: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


@dataclass
class AgentResult:
    summary: str
    tool_calls: list[ToolCall]
    expected_path: str
    expected_content: str


@dataclass
class VerificationResult:
    passed: bool
    checks: list[dict[str, Any]]
    evidence: list[str]


def jsonable(value: Any) -> Any:
    if hasattr(value, "value"):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return {key: jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    return value
