from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from harness.app import build_app
from harness.models import jsonable


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="harness", description="HARNESS0.1 — núcleo local MVP")
    result.add_argument("--db", default="data/harness.sqlite3", help="Ruta de la base SQLite.")
    result.add_argument("--workspace", default="workspace", help="Directorio autorizado para las herramientas locales.")
    result.add_argument("--deliveries", default="entregas", help="Directorio de informes de entrega.")
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="Inicializar almacenamiento y directorios del MVP.")
    run = commands.add_parser("run", help="Crear y ejecutar una tarea acotada.")
    run.add_argument("--title", default="Tarea HARNESS")
    run.add_argument("--task", required=True, help="Descripción de la tarea.")
    run.add_argument("--accept", action="append", default=[], help="Criterio de aceptación; puede repetirse.")
    run.add_argument("--priority", choices=["LOW", "NORMAL", "HIGH", "CRITICAL"], default="NORMAL")
    run.add_argument("--depends-on", action="append", default=[])
    run.add_argument("--allow", action="append", choices=["local.time", "local.list", "local.read", "local.create"], default=[])
    status = commands.add_parser("status", help="Consultar el estado de una tarea.")
    status.add_argument("task_id")
    history = commands.add_parser("history", help="Consultar el historial de una tarea.")
    history.add_argument("task_id")
    res = commands.add_parser("result", help="Consultar la última ejecución de una tarea.")
    res.add_argument("task_id")
    cancel = commands.add_parser("cancel", help="Cancelar una tarea que todavía no sea terminal.")
    cancel.add_argument("task_id")
    cancel.add_argument("--reason", default="Cancelada por solicitud explícita.")
    commands.add_parser("tasks", help="Listar tareas registradas.")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    cwd = Path.cwd().resolve()
    tasks, orchestrator, memory = build_app(args.db, args.workspace, args.deliveries)
    try:
        if args.command == "init":
            print(f"HARNESS0.1 inicializado. Base de datos: {memory.database}")
            return 0
        if args.command == "run":
            task = tasks.create(
                title=args.title,
                description=args.task,
                acceptance_criteria=args.accept or None,
                priority=args.priority,
                dependencies=args.depends_on,
                permissions=args.allow,
                workspace=str((cwd / args.workspace).resolve()),
            )
            finished = orchestrator.run(task.id)
            print(json.dumps(jsonable(finished), ensure_ascii=False, indent=2))
            return 0 if finished.status.value == "COMPLETED" else 2
        if args.command == "status":
            print(json.dumps(jsonable(tasks.get(args.task_id)), ensure_ascii=False, indent=2))
            return 0
        if args.command == "history":
            print(json.dumps(memory.history(args.task_id), ensure_ascii=False, indent=2))
            return 0
        if args.command == "result":
            print(json.dumps(memory.executions(args.task_id), ensure_ascii=False, indent=2))
            return 0
        if args.command == "cancel":
            print(json.dumps(jsonable(tasks.cancel(args.task_id, args.reason)), ensure_ascii=False, indent=2))
            return 0
        if args.command == "tasks":
            print(json.dumps([jsonable(task) for task in tasks.list()], ensure_ascii=False, indent=2))
            return 0
    except (KeyError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
