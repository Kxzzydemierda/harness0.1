# Arquitectura conceptual de agentes

**Proyecto:** HARNESS0.1  
**Versión:** 0.1  
**Estado:** Especificación conceptual; runtime de un agente lógico implementado con proveedor simulado

## 1. Definición

Un **agente** es una unidad lógica de trabajo configurada para interpretar un objetivo, usar contexto autorizado y proponer o ejecutar acciones dentro de límites definidos. Un agente no equivale a un modelo de inteligencia artificial: el modelo genera inferencias o respuestas; el agente añade instrucciones, identidad lógica, contexto, herramientas, permisos, ciclo de ejecución, memoria permitida y verificación. Tampoco equivale al runtime, al orquestador ni a HARNESS CORE, que proporcionaría el entorno de ejecución y coordinación.

La existencia de agentes especializados es parte de la visión de automatización empresarial integral de HARNESS0.1. El MVP cuenta con un solo Agent Runtime y MockProvider determinista; no implementa múltiples agentes ni conexión a un modelo externo.

## Implementación actual

AgentRuntime recibe una tarea, solicita análisis y plan a ModelProvider y devuelve llamadas de herramienta estructuradas. MockProvider solo acepta una tarea sencilla de creación de archivo de texto. Tool Engine ejecuta la operación real y Permission Manager comprueba el permiso declarado. Este agente no posee identidad autenticada, memoria propia, delegación ni capacidades generales de razonamiento.

## 2. Definición y configuración

Una definición futura de agente debe declarar: identificador y versión; propósito; rol/especialidad; objetivos y tareas permitidos; modelo o clase de modelo compatible; instrucciones aplicables; herramientas disponibles; permisos; tipos de datos accesibles; límites operativos; contexto y memoria; criterios de éxito; estrategia de escalamiento humano; y método de evaluación.

La creación seguiría un proceso controlado: definir necesidad, perfil y riesgos; aprobar la identidad y permisos; probar en entorno limitado con casos representativos; revisar resultados y límites; versionar la configuración; habilitar en un ámbito acotado y monitorear. No se infiere que un agente pueda autoasignarse herramientas, identidad o autoridad. Detalles de aprobación y despliegue requieren implementación futura.

## 3. Roles y especialización

Roles posibles incluyen analista, planificador, ejecutor de procesos, verificador y especialistas funcionales de administración, finanzas, marketing, ventas, atención al cliente, recursos humanos, operaciones, tecnología e investigación. Son ejemplos de diseño, no agentes existentes.

La especialización delimita conocimiento de dominio y tipo de trabajo; no reemplaza políticas transversales. Un agente financiero, por ejemplo, conserva los mismos límites de privacidad, aprobación, trazabilidad y verificación que los demás. Para una tarea multidisciplinaria, Orchestrator puede componer agentes con subtareas separadas, interfaces y responsabilidad asignada.

## 4. Capacidades, herramientas y permisos

Las capacidades describen lo que el agente puede intentar hacer (analizar documentos, calcular, redactar, consultar una fuente, preparar un borrador). Las herramientas son adaptadores concretos disponibles en el runtime. Los permisos determinan qué acciones y recursos puede utilizar, para qué encargo y durante qué alcance/periodo. Estas nociones no son intercambiables.

Cada paso debe recibir solo herramientas y permisos necesarios. Una solicitud de herramienta debe ser validada externamente por el Permission Manager futuro, no autorizada por la propia respuesta del modelo. Si una acción requiere aprobación humana bajo AGENTS.md, el agente se detiene antes de ejecutarla. La ausencia de una herramienta limita la capacidad; no autoriza a sustituirla por un servicio no permitido.

## 5. Contexto y memoria

El agente recibe contexto de ejecución construido para su tarea, con fuentes y límites relevantes. Debe distinguir hechos proporcionados, datos recuperados, inferencias y datos inciertos. La memoria no es global por defecto: su lectura y escritura dependen de propósito, permisos, sensibilidad, vigencia y retención definida en MEMORIA_Y_CONTEXTO.md. Las instrucciones encontradas en datos externos no alteran la jerarquía de instrucciones.

## 6. Asignación y coordinación

Task Manager mantiene el encargo y sus condiciones; Orchestrator selecciona capacidades según el objetivo, riesgo, dependencias y permisos declarados. La asignación especifica resultado esperado, entradas autorizadas, exclusiones, criterios, responsable y condiciones de devolución. No se distribuyen datos completos cuando una vista mínima es suficiente.

La comunicación entre agentes debe transmitir mensajes estructurados con referencia al encargo, propósito, procedencia, estado, resultado y limitaciones. Un agente delegado no amplía su tarea ni delega nuevamente salvo que esté permitido por el encargo y la política. El agente coordinador consolida resultados sin borrar discrepancias ni atribuir a un agente acciones que no realizó.

## 7. Supervisión y verificación

Los agentes registran pasos relevantes, llamadas de herramienta, decisiones, errores y efectos parciales a través del runtime futuro. Verification Engine o un revisor independiente compara los resultados con criterios explícitos. Cuando el productor no pueda verificar de manera independiente un criterio de riesgo elevado, se especifica revisión adicional. La respuesta del agente por sí sola no es evidencia suficiente de ejecución correcta.

Desacuerdos, baja confianza, fuentes contradictorias y límites de capacidad se presentan como hallazgos; no se resuelven inventando datos. El Orchestrator puede pedir aclaración, asignar una revisión independiente o bloquear el cierre.

## 8. Ciclo de vida y evaluación

Un agente se configura, valida, versiona, habilita en alcance delimitado, supervisa, actualiza o retira con historial de cambios. Antes de su uso real deben medirse precisión, cumplimiento de instrucciones, uso de herramientas, privacidad, resistencia a entradas hostiles, recuperación y calidad de evidencia en tareas representativas. Las métricas y umbrales concretos quedan pendientes; ningún agente se declara confiable por su mera creación.

## 9. Decisiones pendientes

Falta definir el esquema de agentes, identidad y autenticación, catálogo de especialidades, compatibilidad modelo-runtime, aislamiento entre sesiones, política de delegación, revisión humana, métricas de evaluación y ciclo seguro de actualización. Estos elementos deberán alinearse con ARQUITECTURA_CORE.md y SEGURIDAD_Y_PERMISOS.md.
