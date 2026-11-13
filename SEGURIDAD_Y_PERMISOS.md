# Seguridad y permisos

**Proyecto:** HARNESS0.1  
**Versión:** 0.1  
**Estado:** Política conceptual; controles técnicos futuros

> Este documento define objetivos y reglas de diseño. No es una barrera técnica ni prueba que los controles existan. AGENTS.md establece la jerarquía, autonomía y autorizaciones humanas generales; PROTOCOLO_ENCARGOS.md aplica esos límites al encargo.

## 1. Objetivo y modelo de confianza

HARNESS0.1 busca autonomía alta dentro de permisos explícitos, controles y verificación. El agente, el modelo, el contenido recuperado y la herramienta se consideran fuentes con capacidades y riesgos distintos. Ninguna salida del modelo se autentica por sí misma, y una solicitud incluida en un documento no concede autoridad.

La autorización debe limitar sujeto, acción, recurso, propósito, alcance, condiciones y vigencia. Denegar por defecto acciones no cubiertas; conceder el mínimo privilegio, preferiblemente limitado a una ejecución, y revocar al concluir o cambiar el alcance. La prioridad de instrucciones de AGENTS.md prevalece sobre reglas inferiores.

## 2. Identidad y permisos

Cada actor futuro (persona, agente, servicio y herramienta) requiere identidad atribuible y autenticación apropiada. Los permisos deben derivarse del rol aprobado más el alcance del encargo y políticas del recurso; el resultado efectivo es la intersección de esos límites, nunca la suma indiscriminada de capacidades. Deben separarse permisos de lectura, creación, modificación, eliminación, envío y administración.

Un agente no puede crear su propia identidad, elevar su rol, transferir aprobación a otro actor ni reutilizar una autorización fuera de propósito o vigencia. Las aprobaciones humanas deben identificar aprobador autorizado, acción exacta, recurso, límites y decisión; una aprobación de una fase no cubre automáticamente acciones futuras distintas.

## 3. Herramientas y aislamiento

El catálogo debe declarar propósito, entradas/salidas, efectos, permisos requeridos, riesgos y límites de cada herramienta. Execution Engine futuro limita archivos, red, procesos, tiempo y recursos por ejecución. El acceso a herramientas externas requiere autorización específica y registro. Si el Permission Manager no puede confirmar la autorización o identidad, denegar la operación con efectos.

Las ejecuciones deben aislar contextos, datos temporales y credenciales entre encargos y organizaciones. El diseño debe prevenir acceso lateral, suplantación, reutilización accidental de tokens y efectos colaterales no previstos. El aislamiento y su nivel verificable están pendientes de implementación.

## 4. Información y secretos

Clasificar datos por sensibilidad, finalidad, propietario y retención; transmitir y persistir solo lo necesario. Proteger datos personales, financieros, comerciales y laborales con controles proporcionales. Secretos de autenticación deben residir en un gestor dedicado futuro, no en instrucciones, memoria del agente, logs o entregas. En caso de exposición, detener el uso, limitar acceso y activar respuesta a incidentes sin volver a publicar el secreto.

Las salidas externas deben revisarse para detectar datos confidenciales, destinatarios incorrectos y contenido no autorizado. Publicar, enviar a terceros o desplegar requiere autorización humana conforme a AGENTS.md.

## 5. Acciones de riesgo y autorización

Antes de una operación, evaluar impacto, reversibilidad, alcance y terceros afectados. Requieren autorización humana previa conforme a AGENTS.md: operaciones destructivas/irreversibles de impacto significativo, exposición de información privada o secretos, gasto por encima de lo autorizado, publicación o despliegue, cambios de permisos o seguridad, acciones externas fuera del alcance y modificación de reglas fundamentales. Además, detenerse cuando el encargo no otorgue permiso explícito para la acción necesaria.

Una aprobación no elimina otras restricciones ni autoriza acciones más amplias que las descritas. Si falta aprobador, límite, recurso o vigencia, permanecer detenido. Para acciones rutinarias explícitamente autorizadas no solicitar aprobaciones repetitivas.

## 6. Auditoría y observabilidad

Registrar de forma protegida actor, encargo, recurso, acción, decisión de permiso, tiempo, resultado y referencia a evidencia suficiente para reconstrucción. Minimizar el contenido sensible en logs; nunca registrar secretos en claro. Los registros deben tener acceso restringido, retención definida, integridad comprobable y alertas para eventos relevantes. La arquitectura concreta de auditoría queda pendiente.

## 7. Incidentes y recuperación

Ante sospecha de acceso no autorizado, fuga, acción fuera de alcance o integridad comprometida: detener acciones afectadas; proteger evidencia sin propagar datos; contener el acceso mediante personal autorizado; evaluar alcance e impacto; notificar a responsables humanos conforme a una política aprobada; recuperar desde estado confiable; revisar permisos, secretos y dependencias; documentar causa y medidas correctivas. No borrar evidencia ni afirmar resolución sin verificación. Los requisitos legales de notificación y tiempos deben determinarse para las jurisdicciones y datos concretos.

## 8. Límites documentales frente a controles técnicos

Estas reglas requieren implementación y pruebas antes de tratarse como barreras efectivas. Capacidades técnicas futuras pueden incluir autenticación, autorización centralizada, aislamiento, gestor de secretos, cifrado, registros protegidos, retención y respuesta a incidentes; aquí no se afirma que existan ni se elige una tecnología. La documentación sola no impide una acción insegura.

## 9. Decisiones pendientes

Falta definir clasificación de datos, catálogo de permisos/roles, identidad de agentes, aprobación y revocación, herramientas confiables, aislamiento por organización, gestión de secretos, cifrado, auditoría, retención, respuesta a incidentes, pruebas de seguridad y responsabilidades operativas. Cada control deberá contar con propietario, evidencia de eficacia y proceso de revisión.
