# Ciclo de ejecución

**Proyecto:** HARNESS0.1  
**Versión:** 0.1  
**Estado:** Especificación documental; flujo parcial implementado en el MVP local

> Define el flujo que conecta recepción y entrega. Sus etapas son un proceso lógico y no implican servicios ya existentes. AGENTS.md fija la jerarquía y los límites; PROTOCOLO_ENCARGOS.md define la entidad y sus estados; PROTOCOLO_ENTREGAS.md define el informe final.

## 1. Principios

Cada ejecución pertenece a un encargo identificado, conserva su alcance y permisos, y produce evidencia suficiente para evaluar el resultado. La autonomía es alta dentro de las autorizaciones vigentes. El agente no amplía el objetivo ni interpreta silencio como permiso. Un cambio material de alcance vuelve a análisis y puede requerir nueva aprobación.

Las etapas no son necesariamente procesos separados ni deben mapearse uno a uno con los estados del encargo. Un estado describe situación; una etapa describe trabajo lógico. El MVP conecta análisis, planificación, ejecución, verificación y entrega en un único proceso local; recepción se realiza por la CLI y asignación está fija a un agente lógico. No implementa colas, reintentos automáticos ni persistencia transaccional de cada etapa.

## 2. Etapas

| Etapa | Responsabilidad | Entrada | Salida y avance |
|---|---|---|---|
| RECEPCIÓN | Registrar la solicitud y comprobar que se identifica como encargo. | Solicitud y remitente. | Encargo candidato con ID, título y contenido recibido; pasa a análisis. Si no puede identificarse o registrarse, se declara el impedimento. |
| ANÁLISIS | Leer instrucciones, extraer objetivo, alcance, restricciones, aceptación, dependencias, permisos y riesgos; detectar conflictos y vacíos. | Encargo, reglas aplicables y contexto disponible. | Definición suficientemente clara o lista concreta de aclaraciones. Información faltante que impide actuar bloquea la ejecución. |
| PLANIFICACIÓN | Ordenar pasos, recursos, dependencias, riesgos, validaciones, alternativas seguras y puntos de decisión humana. | Definición analizada y autorizaciones. | Plan proporcional con resultados intermedios y pruebas; el plan no concede permisos. |
| ASIGNACIÓN | Elegir agente o conjunto de agentes con capacidad y autorización apropiadas. | Plan, capacidades declaradas y política de permisos. | Responsable(s), tarea delimitada y contexto mínimo necesario. Si no existe agente elegible, queda bloqueado y se registra la carencia. |
| EJECUCIÓN | Realizar pasos autorizados, mantener el alcance y registrar resultados y efectos parciales. | Tarea asignada, entradas y permisos vigentes. | Artefactos/resultados listos para verificación, o error, bloqueo o necesidad de aprobación documentados. |
| VERIFICACIÓN | Contrastar cada criterio de aceptación con resultado y evidencia. | Resultado, criterios y evidencias. | Criterios como cumple, no cumple o no verificable; identificar corrección necesaria o condición de cierre. |
| CORRECCIÓN | Reparar defectos dentro del alcance y permisos; no ocultar cambios ni efectos previos. | Hallazgos de verificación o errores recuperables. | Resultado corregido que vuelve a verificación, o impedimento/fracaso explicado. Requiere nuevo análisis si cambia el método, riesgo o autorización. |
| ENTREGA | Preparar informe y comunicar estado real, resultados, artefactos, evidencias y pendientes. | Verificación final, decisiones y registro de ejecución. | Informe conforme a PROTOCOLO_ENTREGAS.md y cierre del encargo solo si cumple sus condiciones. |

## 3. Transiciones y controles

Flujo habitual: RECEPCIÓN → ANÁLISIS → PLANIFICACIÓN → ASIGNACIÓN → EJECUCIÓN → VERIFICACIÓN → (CORRECCIÓN → VERIFICACIÓN, cuando haga falta) → ENTREGA.

- Si análisis descubre ambigüedad crítica, falta de permiso o dependencia, la ejecución dependiente no comienza. El encargo pasa al estado correspondiente definido en PROTOCOLO_ENCARGOS.md (BLOQUEADO o REQUIERE APROBACIÓN).
- Si el plan supera el alcance, requiere gasto, efecto externo o acción restringida por AGENTS.md, se detiene antes de esa acción y se solicita aprobación explícita. Una aprobación debe tener alcance y vigencia identificables.
- Asignación y ejecución pueden repetirse solo con motivo y expectativa razonable de éxito; reintentos no deben duplicar efectos. Antes de repetir una operación con efectos parciales, se comprueba su estado.
- Toda corrección vuelve a verificación. El agente no cierra una tarea por haber terminado los pasos ni porque un reintento haya respondido sin error.
- COMPLETADO requiere criterios y condiciones de finalización comprobados, y entrega documentada. FALLIDO requiere que no quede una vía razonable, segura y autorizada. CANCELADO refleja retiro válido. Un bloqueo temporal no se reporta como fracaso terminal.

## 4. Errores, reintentos y bloqueos

Ante error, identificar causa y alcance afectado, preservar evidencia pertinente, valorar consecuencias y probar una alternativa segura solo si hay expectativa razonable de recuperación. Limitar reintentos; el máximo técnico y las políticas de idempotencia quedan pendientes de diseño. Si no se conoce si la acción previa tuvo efecto, no repetir una operación de impacto hasta reconciliar el estado.

Registrar bloqueo con causa, etapa, trabajo parcial, condición para desbloquear, responsable conocido y próximo paso. Si falta información, formular preguntas concretas; si falta permiso, esperar aprobación. No usar nuevas credenciales, herramientas o destinatarios para eludir la barrera.

## 5. Intervención humana

La intervención es obligatoria en los casos de autorización enumerados en AGENTS.md y cuando una ambigüedad crítica, decisión de negocio no delegada o conflicto de instrucciones impida actuar con seguridad. Debe pedirse solo la decisión necesaria y detener únicamente las acciones dependientes; el trabajo independiente y autorizado puede continuar si no agrava el riesgo ni hace inútil la respuesta. La falta de respuesta no se interpreta como consentimiento.

## 6. Persistencia del estado

Conceptualmente debe conservarse, por ejecución: ID y versión del encargo; estado y etapa actuales; responsable; tiempos; plan y cambios justificados; decisiones y aprobaciones referenciadas; pasos ejecutados; resultados; errores y reintentos; evidencias; criterios; y vínculo a la entrega. Cada transición debe llevar actor, motivo y fecha lógica. El registro de cambios debe permitir reconstruir el estado sin sobrescribir hechos anteriores.

El MVP persiste tareas, planes, resultados, ejecuciones y eventos en SQLite. No ofrece historial inmutable, control de concurrencia de ejecuciones, recuperación transaccional completa, retención configurable ni protección contra alteración; esos aspectos siguen pendientes.

## 7. Finalización

El ciclo termina cuando se comunica una entrega válida y el encargo alcanza un estado final según PROTOCOLO_ENCARGOS.md. Una entrega bloqueada o parcialmente exitosa es un cierre informativo, no una declaración de éxito. Una continuación crea una nueva ejecución vinculada o reabre mediante regla explícita futura, revalidando permisos, entradas y criterios.

## 8. Coherencia documental y decisiones pendientes

README.md se actualizó para reflejar el árbol actual y separar el código funcional de las capacidades aspiracionales. El inventario debe actualizarse cuando cambie la estructura. La persistencia actual cubre el MVP local, no los requisitos empresariales de auditoría o disponibilidad.
