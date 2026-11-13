# Arquitectura conceptual de HARNESS CORE

**Proyecto:** HARNESS0.1  
**Versión:** 0.1  
**Estado:** Arquitectura conceptual; primer subconjunto implementado en el MVP local

> Este documento propone responsabilidades lógicas para el núcleo. Los componentes pueden compartir proceso, almacenamiento o despliegue; separarlos en servicios independientes solo se justificará por necesidades verificadas de escala, aislamiento, operación o evolución. Las políticas aquí descritas no son controles técnicos presentes.

## 1. Propósito y principios

HARNESS CORE sería la infraestructura que recibe encargos, coordina agentes y herramientas, conserva estado y contexto, y verifica resultados dentro de permisos. Busca soportar procesos empresariales integrales con autonomía alta, modular y escalable, sin confundir una especificación con capacidad disponible.

Principios de diseño:

- Interfaces explícitas entre responsabilidades; implementación reemplazable donde convenga.
- Mínimo privilegio y contexto mínimo necesario para cada ejecución.
- Estado, decisiones, acciones y evidencias distinguibles y trazables.
- Fallo seguro: ante autorización o estado incierto, detener la acción afectada.
- Idempotencia o reconciliación para operaciones que puedan repetirse.
- Verificación separada de la mera producción de resultados.
- Escalar de un núcleo modular a servicios separados solo con evidencia de necesidad.

## 2. Componentes lógicos

### Implementación actual del MVP

El paquete harness/ implementa Task Manager, Orchestrator, Agent Runtime, interfaz ModelProvider con MockProvider, Tool Engine, Permission Manager básico, Verification Engine y Memory Engine SQLite. Estos módulos son componentes lógicos dentro de un solo proceso Python; no son servicios independientes. Logging se representa por eventos estructurados en SQLite, no por una plataforma de observabilidad. Context Manager y Memory Manager semántico no existen; el estado y la memoria persistente se limitan a tareas e historial operativo. Esta implementación cubre solo la capacidad local descrita en README.md.

| Componente | Responsabilidad | Entradas | Salidas y relaciones |
|---|---|---|---|
| Task Manager | Recibir, validar documentalmente y mantener encargos, relaciones, prioridades y estado de alto nivel. | Solicitud, PROTOCOLO_ENCARGOS.md, identidad del solicitante. | Encargo normalizado y eventos de estado para Orchestrator y State Manager; resultados y entrega al solicitante. |
| Orchestrator | Descomponer el objetivo en pasos coordinados, ordenar dependencias, seleccionar capacidades y manejar el flujo de trabajo. | Encargo analizado, plan, disponibilidad de agentes/herramientas, políticas. | Asignaciones y eventos de flujo al Execution Engine; solicitudes de decisión al humano cuando corresponda. |
| Execution Engine | Ejecutar pasos, controlar límites de ejecución, timeout, cancelación, efectos parciales y reintentos. | Paso autorizado, agente, contexto y herramientas concedidas. | Resultado, errores y metadatos a State Manager, Verification Engine y Logging. No decide por sí solo ampliar permisos. |
| Agent Runtime | Cargar configuración y ejecutar el ciclo de razonamiento/acción de un agente mediante un modelo y contexto limitado. | Definición de agente, prompt/instrucciones aplicables, contexto y capacidades. | Propuestas, llamadas de herramienta y resultados; devuelve control al Execution Engine para autorización de cada acción. |
| Context Manager | Construir el contexto de una ejecución con información pertinente, vigente y permitida. | Encargo, memoria recuperable, documentos y permisos de lectura. | Contexto acotado, procedencia y alertas de conflicto a Agent Runtime; coordina recuperación con Memory Manager. |
| Memory Manager | Administrar memoria temporal y persistente, procedencia, vigencia, acceso, retención y eliminación. | Hechos/evidencias autorizados, consultas, políticas de retención. | Resultados recuperados, actualizaciones trazables o rechazo por falta de acceso; alimenta Context Manager. |
| Tool Manager | Inventariar herramientas, describir capacidades/riesgos, validar parámetros y servir adaptadores. | Solicitud de acción, catálogo, autorización emitida por Permission Manager. | Resultado y metadatos al Execution Engine; no concede permisos por sí mismo. |
| Permission Manager | Resolver identidad, permisos efectivos, alcance, vigencia, aprobaciones y límites por recurso/acción. | Identidad, solicitud de acción, política, autorización humana verificable. | Permitir, denegar o requerir aprobación; evidencia de decisión para State Manager y Logging. Es punto de control técnico futuro. |
| Verification Engine | Evaluar artefactos y evidencias contra criterios definidos, usando verificaciones automatizadas o humanas según el caso. | Resultado, criterios, evidencia y método de comprobación. | Cumple / No cumple / No verificable, hallazgos y solicitud de corrección; informa Task Manager y Orchestrator. |
| State Manager | Mantener transiciones consistentes, versiones, relaciones y eventos auditables de encargo y ejecución. | Eventos de los componentes, actor, motivo y tiempo. | Estado vigente e historial para el resto; rechaza transiciones inválidas conforme a reglas configuradas. |
| Logging y observabilidad | Registrar eventos operativos necesarios para diagnóstico, auditoría y métricas con controles de privacidad. | Eventos, errores, decisiones y métricas minimizadas. | Registros consultables y alertas autorizadas; soporte a State Manager, seguridad y operación. No debe registrar secretos en claro. |

## 3. Flujo de referencia

1. Task Manager registra y analiza la solicitud conforme a PROTOCOLO_ENCARGOS.md.
2. Orchestrator planifica la secuencia y delegaciones; la planificación no representa autorización.
3. Context Manager obtiene solo información permitida; Memory Manager aporta procedencia y vigencia.
4. Execution Engine selecciona un agente en Agent Runtime y limita la ejecución al paso asignado.
5. Cada acción de herramienta pasa por Tool Manager y una decisión de Permission Manager antes del efecto.
6. State Manager y Logging registran transiciones, decisiones y resultados con controles de acceso.
7. Verification Engine comprueba criterios y evidencia; puede devolver hallazgos a Orchestrator para corrección.
8. Task Manager prepara el cierre; la entrega sigue PROTOCOLO_ENTREGAS.md.

Un componente puede invocar directamente otro mediante interfaz local en la primera implementación; no se requiere mensajería distribuida si una arquitectura modular simple cumple calidad, aislamiento y escala.

## 4. Límites, fallos y seguridad

Los componentes no listados como implementados siguen siendo conceptuales. El MVP sí valida el permiso declarado antes de cada herramienta local y verifica las rutas del workspace, pero no provee identidad, aislamiento de proceso, almacenamiento inmutable o controles suficientes para operaciones empresariales. En la implementación futura, si el servicio de permisos o el estado confiable no está disponible, las acciones con efectos deberán denegarse de forma segura.

Los errores deben propagarse como resultado explícito con correlación a encargo y paso; reintentos requieren evaluación de idempotencia o reconciliación. La pérdida de contexto o incertidumbre del efecto debe marcarse, no ocultarse.

## 5. Decisiones técnicas pendientes

Quedan por seleccionar tras prototipos y requisitos: límites de módulos/procesos, interfaces y formatos, base de datos y consistencia, cola o ejecución síncrona, identidad y autenticación, aislamiento por tenant, proveedor/modelo, política de memoria, gestión de secretos, límites de recursos, estrategia de observabilidad, copias y recuperación, despliegue y evaluación de rendimiento/seguridad. Ninguna decisión se declara resuelta ni implementada aquí.
