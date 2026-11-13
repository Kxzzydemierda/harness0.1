# Protocolo de entregas

**Proyecto:** HARNESS0.1  
**Versión:** 0.1  
**Estado:** Especificación documental inicial

> Este protocolo define cómo comunicar y evidenciar el resultado de un encargo. No implementa almacenamiento, validación ni controles técnicos. Se aplica junto con AGENTS.md y PROTOCOLO_ENCARGOS.md.

## 1. Propósito y alcance

Una entrega es el registro verificable del trabajo realizado frente a un encargo. Debe permitir que solicitantes, agentes posteriores y revisores entiendan qué se hizo, qué quedó pendiente y con qué evidencia. Se aplica a tareas documentales, administrativas, financieras, comerciales, operativas, tecnológicas y de investigación; el formato se adapta al tipo de resultado sin omitir los campos esenciales.

La entrega no convierte un resultado parcial en éxito ni autoriza acciones posteriores. El estado del encargo se rige por PROTOCOLO_ENCARGOS.md y la jerarquía y límites de AGENTS.md.

## 2. Estructura de una entrega

Cada informe se guarda en entregas/ con nombre único y descriptivo asociado al identificador, por ejemplo 002-prueba-hermes.md. No se sobrescribe una entrega previa; una corrección material genera una nueva versión claramente enlazada.

El informe contiene:

| Campo | Contenido |
|---|---|
| Identificador y título del encargo | ID y nombre conforme al encargo; señalar si el ID es provisional. |
| Estado del encargo | Registrar un estado definido por PROTOCOLO_ENCARGOS.md, como COMPLETADO, FALLIDO, CANCELADO o BLOQUEADO. BLOQUEADO indica espera y no es terminal; un estado no terminal se presenta como cierre informativo. |
| Clasificación de la entrega | EXITOSA, PARCIALMENTE EXITOSA, FALLIDA o BLOQUEADA, según los resultados y la evidencia; no sustituye el estado del encargo. |
| Objetivo y resumen | Resultado buscado y resumen factual de lo ejecutado. |
| Archivos y artefactos | Rutas creadas, modificadas o eliminadas; indicar “ninguno” si aplica. No exponer datos sensibles en el informe. |
| Evidencias | Referencias reproducibles a observaciones, registros, capturas, cálculos o salidas pertinentes; distinguir evidencia disponible de inferencia. |
| Pruebas y validaciones | Qué se comprobó, método, resultado y limitaciones. “No ejecutada” no equivale a aprobada. |
| Aceptación | Lista de criterios, estado (Cumple / No cumple / No verificable), evidencia asociada y pendientes. |
| Errores y limitaciones | Fallos, efectos parciales, riesgos residuales, dependencias o restricciones encontradas. |
| Continuidad | Decisiones, entradas o permisos que faltan y el siguiente paso seguro para retomar, si hace falta. |
| Herramientas relevantes | Herramientas efectivamente usadas; no registrar como usadas las solo planeadas. |

## 3. Estados de entrega

El estado informa el resultado observado, no sustituye el estado del encargo:

- **EXITOSA:** objetivo y condiciones de finalización satisfechos; todos los criterios requeridos comprobados con evidencia.
- **PARCIALMENTE EXITOSA:** se obtuvo un resultado útil, pero uno o más criterios siguen pendientes o no verificables; se explica qué parte sí se completó.
- **FALLIDA:** no se alcanzó un resultado utilizable dentro de las condiciones autorizadas, tras evaluar alternativas razonables.
- **BLOQUEADA:** no puede continuarse por una condición externa o falta de acceso, aprobación, información o dependencia. Se indica explícitamente si no se ejecutó la prueba o actividad prevista.

Una actividad no realizada debe registrarse como no realizada, nunca como evidencia negativa o resultado de prueba.

## 4. Evidencia y validez

Una entrega es válida cuando:

1. Identifica sin ambigüedad el encargo relacionado y el estado real.
2. Resume el trabajo realizado y enumera los artefactos afectados.
3. Vincula cada criterio de aceptación con una comprobación o declara por qué queda pendiente.
4. Separa hechos observados, interpretaciones y limitaciones.
5. Registra fallos, efectos parciales, dependencias y autorizaciones relevantes.
6. No contiene afirmaciones de pruebas, accesos o acciones que no ocurrieron.
7. Respeta privacidad, permisos y límites de AGENTS.md.
8. Está guardada bajo entregas/ sin reemplazar informes previos.

Si falta evidencia crítica, clasificar la entrega como parcial o bloqueada, explicar el faltante y no declarar el criterio cumplido. Las aprobaciones humanas se identifican por decisión, alcance y referencia verificable cuando sea posible; este requisito documental no constituye un mecanismo técnico de autenticación.

## 5. Relación con el ciclo de encargo

La entrega se prepara después de verificar el resultado, incluso cuando el resultado sea fallido o bloqueado. El agente comunica el resumen al solicitante y enlaza el informe. Para una continuación, el nuevo agente debe leer el informe y revalidar que contexto, recursos, dependencias y permisos siguen vigentes; no debe presumir que una autorización anterior sigue aplicando a un alcance modificado.

## 6. Decisiones futuras

Quedan por definir en la implementación: esquema estructurado, almacenamiento y versionado, vínculo automático con estados del encargo, retención de evidencias, tratamiento de evidencias sensibles y validación técnica. Este documento no presume esas capacidades implementadas.
