from __future__ import annotations

from pathlib import Path

from harness.agents import AgentRuntime
from harness.governance import PermissionManager
from harness.memory import MemoryEngine
from harness.orchestrator import Orchestrator
from harness.providers import MockProvider
from harness.tasks import TaskManager
from harness.tools import ToolEngine
from harness.verification import VerificationEngine


def build_app(database: str | Path, workspace: str | Path, deliveries: str | Path) -> tuple[TaskManager, Orchestrator, MemoryEngine]:
    memory = MemoryEngine(database)
    tasks = TaskManager(memory)
    permissions = PermissionManager(memory)
    tools = ToolEngine(workspace, permissions, memory)
    runtime = AgentRuntime(MockProvider())
    verification = VerificationEngine(tools)
    orchestrator = Orchestrator(tasks, runtime, tools, verification, memory, deliveries)
    return tasks, orchestrator, memory
