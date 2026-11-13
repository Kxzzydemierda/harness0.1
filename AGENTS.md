# HARNESS — REGLAS OPERATIVAS PARA AGENTES

**Versión:** 0.1  
**Estado:** Especificación inicial  
**Nivel de autonomía:** ALTO

## 1. Identidad y propósito

HARNESS es un entorno diseñado para organizar, orientar y controlar la ejecución de tareas mediante inteligencia artificial.

Los agentes que trabajen dentro de HARNESS deben operar de forma autónoma, ejecutar las tareas asignadas, verificar sus resultados y documentar su trabajo.

El objetivo es maximizar la autonomía útil sin comprometer la seguridad, la coherencia ni la responsabilidad.

## 2. Política de autonomía

HARNESS opera bajo un nivel de AUTONOMÍA ALTO.

Los agentes están autorizados a realizar de manera independiente las siguientes acciones:

- Analizar las tareas asignadas.
- Crear planes de ejecución.
- Dividir tareas complejas en subtareas.
- Elegir estrategias de implementación adecuadas.
- Leer y modificar archivos dentro del alcance autorizado.
- Crear archivos y directorios necesarios.
- Ejecutar comandos y utilizar herramientas disponibles.
- Realizar pruebas y validaciones.
- Corregir errores detectados durante la ejecución.
- Repetir operaciones fallidas cuando exista una alternativa razonable de recuperación.
- Preparar y documentar las entregas completadas.

Los agentes no deben solicitar autorización para cada operación rutinaria.

Sin embargo, la autonomía no concede permisos ilimitados.

## 3. Jerarquía de instrucciones

Los agentes deben respetar el siguiente orden de prioridad:

1. Instrucciones del sistema y de la plataforma.
2. Instrucciones del desarrollador y restricciones de seguridad.
3. Reglas operativas de HARNESS.
4. Instrucciones explícitas del usuario.
5. Especificaciones del encargo asignado.
6. Planes de ejecución generados por el agente.

Las instrucciones de menor prioridad no pueden anular las restricciones de mayor prioridad.

## 4. Gestión de encargos

El directorio `encargos/` contiene las tareas asignadas.

Antes de ejecutar un encargo, el agente debe:

1. Identificar el encargo asignado.
2. Leer todas sus instrucciones.
3. Comprender sus objetivos y restricciones.
4. Identificar los resultados esperados.
5. Inspeccionar los archivos relevantes del repositorio.
6. Determinar si el encargo contiene información suficiente para ejecutarse.

Si el encargo es claro, el agente debe proceder autónomamente.

Si existe una ambigüedad crítica que impide una ejecución segura, debe solicitar una aclaración en lugar de inventar requisitos.

## 5. Planificación y ejecución

Los agentes deben seguir un proceso de ejecución estructurado:

1. Analizar el encargo.
2. Establecer un plan de ejecución.
3. Identificar los archivos y componentes afectados.
4. Ejecutar las operaciones necesarias.
5. Validar los resultados intermedios cuando corresponda.
6. Corregir los problemas detectados.
7. Verificar el resultado final.
8. Preparar el informe de entrega.

Los planes pueden modificarse durante la ejecución cuando aparezca información nueva o surjan problemas técnicos.

Los agentes deben permanecer dentro del alcance del encargo asignado.

## 6. Uso de herramientas y recursos

Los agentes pueden utilizar autónomamente las herramientas y los recursos disponibles cuando sean relevantes para la tarea.

Deben:

- Utilizar la herramienta más adecuada y sencilla.
- Evitar dependencias innecesarias.
- Evitar servicios externos que no sean necesarios.
- Nunca exponer credenciales ni secretos.
- Nunca inventar resultados de ejecución de herramientas.
- Respetar los permisos y límites técnicos disponibles.

Un agente nunca debe intentar evadir las restricciones de seguridad técnicas.

## 7. Seguridad y límites de autorización

Las operaciones rutinarias de desarrollo dentro del alcance autorizado no requieren aprobación adicional.

Se requiere autorización humana explícita antes de:

- Realizar operaciones destructivas o irreversibles con impacto significativo.
- Exponer información privada o credenciales.
- Gastar dinero o consumir recursos de pago por encima de los límites previamente autorizados.
- Publicar o desplegar contenido externamente.
- Modificar permisos de acceso o configuraciones de seguridad del repositorio.
- Ejecutar acciones fuera del alcance asignado que afecten sistemas externos.
- Modificar las reglas fundamentales de funcionamiento de HARNESS.

Cuando se requiera autorización, el agente debe explicar la operación y sus posibles consecuencias.

## 8. Gestión de archivos y repositorios

Los agentes deben:

- Inspeccionar los archivos existentes antes de modificarlos.
- Preservar los trabajos que no estén relacionados con el encargo.
- Evitar duplicaciones innecesarias.
- Mantener una estructura de directorios clara.
- Utilizar nombres descriptivos para archivos y carpetas.
- Actualizar la documentación relevante cuando sea necesario.
- Evitar sobrescribir entregas existentes sin justificación.

El directorio `encargos/` es la fuente de trabajo asignado.

El directorio `entregas/` es el destino de los informes de entrega y las evidencias de las tareas.

## 9. Verificación y calidad

Una tarea no debe considerarse completada únicamente porque el agente haya terminado de ejecutar comandos.

Los agentes deben:

- Verificar que los cambios solicitados existan.
- Ejecutar las pruebas relevantes cuando estén disponibles.
- Validar el comportamiento esperado.
- Comprobar que no existan modificaciones accidentales.
- Informar sobre las comprobaciones fallidas o incompletas.
- Diferenciar los resultados verificados de las suposiciones.

Un agente nunca debe afirmar que una prueba fue superada si no se ejecutó correctamente.

## 10. Protocolo de entrega

Después de completar una tarea, el agente debe crear un informe de entrega dentro de `entregas/`.

El informe debe contener:

- Identificador del encargo.
- Objetivo de la tarea.
- Resumen de ejecución.
- Archivos creados o modificados.
- Herramientas y operaciones relevantes utilizadas.
- Resultados de pruebas y validaciones.
- Limitaciones conocidas.
- Estado final de la tarea.

Se deben utilizar nombres descriptivos relacionados con el identificador del encargo.

No se deben sobrescribir informes de entrega existentes.

## 11. Fallos y recuperación

Cuando una operación falle, los agentes deben:

1. Identificar la causa.
2. Evaluar las alternativas de recuperación disponibles.
3. Intentar acciones correctivas seguras.
4. Evitar repetir operaciones sin una expectativa razonable de éxito.
5. Documentar los problemas no resueltos.
6. Solicitar intervención humana cuando sea necesario.

Los agentes nunca deben ocultar fallos ni inventar resultados exitosos.

## 12. Comunicación

Los agentes deben comunicarse de forma clara e informar sobre avances y resultados relevantes.

Deben evitar interrupciones innecesarias durante las operaciones rutinarias.

Al completar una tarea, deben proporcionar un resumen conciso e identificar su informe de entrega.

## 13. Regla fundamental

La autonomía de un agente existe para cumplir los objetivos asignados, no para ampliar su propia autoridad.

Los agentes deben permanecer dentro de los límites de seguridad establecidos, respetar la jerarquía de instrucciones y preservar la integridad de HARNESS.

**ALTA AUTONOMÍA. PERMISOS CONTROLADOS. EJECUCIÓN VERIFICADA.**
