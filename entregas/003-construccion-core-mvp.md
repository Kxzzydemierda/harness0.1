# Entrega 003 — Primer CORE funcional

**Encargo relacionado:** solicitud de construcción del CORE recibida antes de que el MVP estuviera disponible; no se registró como tarea del propio sistema.  
**Prueba integral asociada:** ENC-2026-0005.  
**Estado del trabajo:** COMPLETADO
**Clasificación de entrega:** EXITOSA

## Objetivo

Implementar el primer núcleo local ejecutable de HARNESS0.1, con un ciclo de tareas limitado, herramientas seguras, permisos explícitos, verificación real, persistencia SQLite, CLI y pruebas.

## Resumen de resultados

Se implementó un paquete modular de Python 3.12 que ejecuta en un solo proceso. El flujo funcional actual recibe tareas desde la CLI, las analiza y planifica con MockProvider, ejecuta herramientas reales dentro de un workspace autorizado, verifica los artefactos leyendo el archivo, guarda el historial y genera informes en entregas/.

El MVP no usa Hermes, frameworks externos de agentes ni un modelo remoto. No se afirma que exista automatización empresarial general.

## Decisiones de arquitectura

- Módulos lógicos dentro de un proceso; no se dividió el MVP en servicios.
- Dataclasses y validaciones explícitas de Python; no se añadió Pydantic.
- SQLite para tareas, estados, secuencias de ID por base, planes, ejecuciones, resultados, errores y eventos.
- MockProvider determinista y limitado a crear archivos de texto .txt, .md o .csv. ModelProvider es una interfaz; no conecta un modelo externo.
- Las herramientas disponibles son hora UTC, listado, lectura y creación sin sobrescritura. Las rutas se resuelven y confinan al workspace.
- Los permisos se conceden explícitamente al crear la tarea. La falta de permiso se registra y detiene la acción; no hay flujo seguro de aprobación o reanudación en la CLI.
- Los estados de código son PENDING, ANALYZING, PLANNING, EXECUTING, VERIFYING, REQUIRES_APPROVAL, BLOCKED, COMPLETED, FAILED y CANCELLED. Se mantuvo REQUIRES_APPROVAL del protocolo existente, que no estaba en la lista inicial del nuevo encargo; PLANNING representa una etapa interna.
- La prioridad y las dependencias se conservan. Una dependencia no completada bloquea la ejecución.
- Las entregas usan nombres únicos por ejecución y no sobrescriben informes anteriores.

## Archivos creados

- harness/__init__.py
- harness/agents.py
- harness/app.py
- harness/cli.py
- harness/governance.py
- harness/memory.py
- harness/models.py
- harness/orchestrator.py
- harness/providers.py
- harness/tasks.py
- harness/tools.py
- harness/verification.py
- requirements-dev.txt
- tests/unit/test_tasks.py
- tests/unit/test_tools.py
- tests/unit/test_verification.py
- tests/integration/test_workflow.py
- entregas/enc-2026-0001-entrega.md a entregas/enc-2026-0005-entrega.md

## Archivos modificados

- .gitignore: exclusiones para caché, entorno virtual, base y workspace local.
- README.md: estado real del MVP, estructura, límites e instrucciones para Windows.
- PROTOCOLO_ENCARGOS.md: identificadores, registro de estados y componentes actualizados según lo implementado.
- CICLO_EJECUCION.md, ARQUITECTURA_CORE.md, ARQUITECTURA_AGENTES.md, MEMORIA_Y_CONTEXTO.md y SEGURIDAD_Y_PERMISOS.md: se actualizaron para distinguir el subconjunto implementado de los diseños futuros.
- AGENTS.md y PROTOCOLO_ENTREGAS.md no se modificaron.

## Pruebas y validaciones

- Python 3.12.10: compilación de harness y tests con compileall, completada.
- Pytest: 20 pruebas pasaron.
- La suite cubre transiciones e IDs, persistencia, validación, rutas fuera del workspace, archivos preexistentes, permisos, dependencias, reanudación sin sobrescribir una entrega, criterios no verificables y el ciclo integral.
- Prueba real por CLI: ENC-2026-0005 terminó COMPLETED. Se creó informe.txt en un workspace dedicado, se ejecutaron create_file y read_file, ambos criterios fueron verificados y se generó esta evidencia relacionada en entregas/enc-2026-0005-entrega.md. El archivo tenía 408 bytes; su SHA-256 local fue 3C4186B0B21B42B3BA6553173B36ED80C5908766E21D0B347FAD14113FA8AB04.
- El historial SQLite de ENC-2026-0005 conserva creación, análisis, plan, permisos, las dos llamadas de herramientas, verificación, entrega y transición a COMPLETED. La base y el workspace de validación están excluidos del control de versiones.

## Criterios de aceptación

- CORE, gestión de tareas, runtime de un agente, interfaz de proveedor y MockProvider: **Cumple** dentro del alcance limitado del MVP.
- Orquestación, herramientas locales y comprobación de permisos: **Cumple** para las capacidades incluidas.
- Verificación independiente de la afirmación del agente: **Cumple**; el archivo se leyó y comparó con el contenido esperado.
- Historial SQLite, consulta por CLI y entrega automática: **Cumple** en la prueba integral.
- Seguridad para operaciones empresariales generales: **Pendiente**; este MVP solo permite las herramientas locales descritas.

## Errores y limitaciones

MockProvider solo reconoce tareas sencillas de creación de archivo; no entiende encargos generales. No hay proveedor real, agentes múltiples, asignación dinámica, búsqueda semántica, API, interfaz gráfica, integración empresarial, aprobador autenticado, retención configurable ni registros inmutables. La secuencia de identificadores es única dentro de una base SQLite, no entre bases independientes. Las prioridades se guardan pero todavía no ordenan una cola.

La lista de estados de implementación incluye REQUIRES_APPROVAL para mantener coherencia con PROTOCOLO_ENCARGOS.md, aunque esa etiqueta no figuraba en la lista inicial del encargo técnico. La documentación registra esta decisión. No se modificaron las reglas fundamentales de AGENTS.md.

## Cómo iniciar

Desde la raíz del repositorio, con Python 3.12:

~~~powershell
python -m harness.cli init
python -m harness.cli run --title "Informe de estado" --task "Crear un archivo llamado informe.txt y escribir un informe del estado de HARNESS0.1" --accept "El archivo existe." --accept "El contenido coincide con el contenido esperado." --allow local.create --allow local.read
~~~

Para instalar Pytest de desarrollo y ejecutar la suite:

~~~powershell
python -m pip install -r requirements-dev.txt
python -m pytest
~~~

## Continuidad y próximo paso

Implementar una autorización humana autenticada con alcance, registro y reanudación segura de tareas; después, diseñar un adaptador de proveedor real detrás de ModelProvider, con pruebas de seguridad y sin habilitar acciones externas por defecto.
