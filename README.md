# HARNESS0.1

HARNESS0.1 es un proyecto en etapa inicial que aspira a convertirse en un sistema integral de automatización empresarial mediante inteligencia artificial. Su visión es que una empresa pueda coordinar y automatizar sus operaciones de principio a fin con agentes especializados y autónomos, reduciendo al mínimo la intervención humana cuando sea apropiado.

> **Estado del proyecto:** HARNESS0.1 incluye un MVP local inicial en Python con ejecución de tareas limitadas mediante MockProvider, herramientas locales con permisos explícitos, verificación y persistencia SQLite. No conecta modelos externos ni implementa automatización empresarial integral.

## Visión

Construir una infraestructura capaz de comprender objetivos empresariales, organizar el trabajo entre distintas áreas y coordinar agentes de inteligencia artificial para llevar adelante procesos completos. HARNESS0.1 no se concibe como un chatbot, un asistente aislado ni únicamente como un orquestador de agentes, sino como una base para automatizar operaciones empresariales integrales.

## Objetivos

- Avanzar hacia la automatización coordinada de procesos empresariales de principio a fin.
- Permitir la colaboración de agentes especializados en distintas áreas y tareas.
- Mantener una arquitectura modular que pueda evolucionar junto con las necesidades de una empresa.
- Reducir tareas manuales y la intervención humana rutinaria, preservando supervisión y responsabilidad.
- Hacer que las acciones puedan ejecutarse dentro de permisos definidos y verificarse antes de considerarse completas.

## Filosofía

HARNESS0.1 prioriza resultados útiles, claridad de responsabilidades y límites explícitos de autorización. La autonomía debe servir para cumplir objetivos asignados y no para ampliar permisos. El desarrollo debe ser incremental, verificable y documentado; los resultados esperados deben distinguirse de las capacidades que todavía son aspiracionales.

## Áreas empresariales

A largo plazo, el sistema pretende gestionar y coordinar procesos de las siguientes áreas:

- Administración
- Finanzas
- Marketing
- Ventas
- Atención al cliente
- Recursos humanos
- Operaciones
- Tecnología
- Investigación

La inclusión de estas áreas describe el alcance buscado, no funcionalidades actualmente disponibles.

## Arquitectura conceptual

La arquitectura futura se plantea como un conjunto de módulos escalables que podrían evolucionar de forma independiente y coordinarse mediante interfaces y políticas comunes:

1. **Objetivos y solicitudes:** representación de metas, tareas y criterios de finalización.
2. **Coordinación:** distribución y seguimiento del trabajo entre agentes y procesos.
3. **Agentes especializados:** unidades enfocadas en tareas o dominios empresariales concretos.
4. **Integraciones y contexto:** conexión controlada con la información y los sistemas que cada proceso necesite.
5. **Permisos y gobernanza:** definición de límites, aprobaciones y responsabilidades para cada acción.
6. **Verificación y seguimiento:** revisión de resultados, registro de evidencias y comunicación de limitaciones.

Estos módulos describen una arquitectura objetivo. El MVP implementa un subconjunto acotado, identificado a continuación; no representa la arquitectura empresarial completa ni integraciones existentes.

## Implementación funcional disponible

El MVP actual tiene un único flujo determinista para crear, leer y listar archivos de texto dentro de un workspace configurado. Incorpora Task Manager, Agent Runtime con MockProvider, una interfaz ModelProvider extensible, Orchestrator, Tool Engine, comprobaciones básicas de permisos, verificación por lectura real, historial SQLite y entregas Markdown. La CLI permite ejecutar y consultar tareas.

Las herramientas implementadas no permiten eliminar ni sobrescribir archivos, ni acceder a rutas fuera del workspace. Los permisos se declaran al crear el encargo; una operación sin permiso queda en **REQUIRES_APPROVAL**. Esta comprobación es básica y local, no una identidad autenticada ni un control de seguridad suficiente para operaciones empresariales reales.

Los estados internos usan nombres en inglés para el MVP: **PENDING**, **ANALYZING**, **PLANNING**, **EXECUTING**, **VERIFYING**, **COMPLETED**, **BLOCKED**, **FAILED** y **CANCELLED**. También se incluye **REQUIRES_APPROVAL**, requerido por PROTOCOLO_ENCARGOS.md aunque no aparecía en la lista inicial del encargo de implementación. **PLANNING** es una etapa interna adicional. No se implementa todavía un mecanismo seguro de aprobación o reanudación desde la CLI.

MockProvider solo admite tareas sencillas que soliciten crear un archivo .txt, .md o .csv; su análisis y contenido son deterministas. ModelProvider define una interfaz, pero no hay proveedor de modelos externo conectado. No hay múltiples agentes, memoria semántica, integraciones empresariales, despliegue ni operación autónoma general.

## Autonomía empresarial

La meta es alcanzar una autonomía alta que permita ejecutar procesos empresariales completos con poca intervención humana rutinaria. Esa autonomía estará limitada por permisos explícitos, controles de seguridad, verificaciones de resultados y puntos de intervención humana cuando una decisión, un riesgo o una ambigüedad lo requiera.

La autonomía no implica acceso ilimitado ni ejecución sin supervisión. Cada acción deberá mantenerse dentro del alcance autorizado, y el estado de una tarea deberá basarse en resultados comprobados.

## Metodología de desarrollo

El desarrollo de HARNESS0.1 seguirá un enfoque incremental y orientado a encargos:

1. Definir objetivos, alcance y restricciones.
2. Dividir el trabajo en tareas manejables.
3. Diseñar o implementar únicamente lo necesario para cada etapa.
4. Validar los resultados con comprobaciones pertinentes.
5. Corregir los problemas detectados y documentar las limitaciones.
6. Registrar las entregas sin sobrescribir trabajos anteriores.

Las capacidades futuras se incorporarán de manera progresiva. Las decisiones de diseño deberán favorecer modularidad, escalabilidad, seguridad y verificabilidad.

## Estructura actual del repositorio

HARNESS0.1/ contiene la documentación de diseño y el MVP local:

~~~text
HARNESS0.1/
├── AGENTS.md
├── README.md
├── .gitignore
├── ARQUITECTURA_AGENTES.md
├── ARQUITECTURA_CORE.md
├── CICLO_EJECUCION.md
├── MEMORIA_Y_CONTEXTO.md
├── PROTOCOLO_ENCARGOS.md
├── PROTOCOLO_ENTREGAS.md
├── SEGURIDAD_Y_PERMISOS.md
├── requirements-dev.txt
├── harness/
│   ├── __init__.py
│   ├── agents.py
│   ├── app.py
│   ├── cli.py
│   ├── governance.py
│   ├── memory.py
│   ├── models.py
│   ├── orchestrator.py
│   ├── providers.py
│   ├── tasks.py
│   ├── tools.py
│   └── verification.py
├── tests/
│   ├── integration/
│   │   └── test_workflow.py
│   └── unit/
│       ├── test_tasks.py
│       ├── test_tools.py
│       └── test_verification.py
├── encargos/
│   └── 001-verificar-estructura.md
└── entregas/
    ├── .gitkeep
    ├── 002-prueba-hermes.md
    ├── enc-2026-0001-entrega.md
    ├── enc-2026-0002-entrega.md
    ├── enc-2026-0003-entrega.md
    ├── enc-2026-0004-entrega.md
    ├── enc-2026-0005-entrega.md
    └── 003-construccion-core-mvp.md
~~~

data/ guarda la base SQLite, workspace/ es el directorio local de herramientas y .harness-run/ se usa para validación local. Se crean al ejecutar HARNESS y están excluidos del control de versiones.

## Ejecución local en Windows

Se requiere Python 3.12 o superior. El runtime usa únicamente la biblioteca estándar. Desde la raíz del repositorio:

~~~powershell
python --version
python -m harness.cli init
python -m harness.cli run --title "Informe de estado" --task "Crear un archivo llamado informe.txt y escribir un informe del estado de HARNESS0.1" --accept "El archivo existe." --accept "El contenido coincide con el contenido esperado." --allow local.create --allow local.read
~~~

La salida muestra el identificador de tarea. El informe de entrega se genera en entregas/; el archivo de trabajo queda en workspace/. Sin --allow local.create no se crea el archivo y la tarea queda esperando aprobación. Si se permite crear pero no leer, el archivo puede crearse, pero la verificación queda detenida y requiere el permiso local.read.

Para consultar tareas, estado, historial y resultado:

~~~powershell
python -m harness.cli tasks
python -m harness.cli status ID_DE_TAREA
python -m harness.cli history ID_DE_TAREA
python -m harness.cli result ID_DE_TAREA
~~~

Para ejecutar las pruebas de desarrollo:

~~~powershell
python -m pip install -r requirements-dev.txt
python -m pytest
~~~

## Estado actual

HARNESS0.1 está en una etapa inicial de diseño e implementación. El MVP ejecuta una capacidad limitada y verificable; no constituye una promesa de automatización empresarial completa. Los componentes conceptuales descritos en la documentación deben considerarse futuros salvo donde se identifique expresamente la implementación actual.
