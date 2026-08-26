# (a) Tabla completa de clasificación por capas

**Fecha del análisis:** 2026-08-26
**Proyecto analizado:** EntreVoces (d:\PROYECTOS\Habitat\Codigo_Proyecto)

## Leyenda de capas

- **Capa 1 (Meta-framework):** Agnóstico de proyecto. Reutilizable en cualquier proyecto futuro con agentes IA.
- **Capa 2 (Domain-pack):** Específico al TIPO de proyecto (hardware+firmware+audio+IoT backend). Reutilizable en proyectos similares.
- **Capa 3 (Instancia):** Hechos específicos de EntreVoces. No reutilizable tal cual.

## Leyenda de acciones

- **MANTENER:** No requiere cambios para el proyecto actual.
- **GENERALIZAR:** Extraer versión parametrizada con `{{placeholders}}` a la plantilla.
- **FUSIONAR:** Consolidar con otro documento para eliminar redundancia.
- **MOVER:** Reubicar dentro de la estructura propuesta.
- **ELIMINAR:** Borrar por ser redundante o estar reemplazado.
- **RENOMBRAR:** Cambiar nombre para consistencia.

---

## Archivos de raíz y configuración

| Archivo | Capa | Acción | Notas |
|---|---|---|---|
| `AGENTS.md` | 1+3 | GENERALIZAR | Estructura (§1-§7) es Capa 1. Contenido (español, PostgreSQL, WAV) es Capa 3. Extraer plantilla con `{{}}` |
| `PROJECT_STATE.md` | 1+3 | GENERALIZAR | Formato (§1-§10, protocolo §9) es Capa 1. Datos (GPIO, hitos) son Capa 3 |
| `.env.ejemplo` | 1+3 | GENERALIZAR | Patrón `PREFIJO_VARIABLE=` es Capa 1. Variables `ENTREVOCES_*` son Capa 3 |
| `.agents/claude.yaml` | 1+3 | GENERALIZAR | Estructura (modelo, contexto, capacidades) es Capa 1. Valores son Capa 3 |

## Reglas (.agents/rules/)

| Archivo | Capa | Acción | Notas |
|---|---|---|---|
| `.agents/rules/claude.md` | 1+3 | GENERALIZAR + FUSIONAR con superpowers | §2 (modo colaborativo), §3 (contexto), §4 (skills), §5 (secretos), §8 (comunicación) = Capa 1. §6-7 (español, arquitectura) repiten AGENTS.md. §13 y §15 se fusionan con superpowers |
| `.agents/rules/entrevoces_mvp.md` (raíz) | 3 | ELIMINADO | Ya ejecutado en Fase 1. Era copia comprimida de AGENTS.md §1-5 |
| `.agents/rules/excepciones_nominales.md` | 1+3 | GENERALIZAR | Formato de tabla (nombre/ubicación/razón/alternativa) es Capa 1. Filas concretas son Capa 3 |
| `entrega_antigravity/.agents/rules/entrevoces_mvp.md` | 3 | MANTENER | Necesaria como regla always-on del workspace portable Antigravity |

## Skills (.agents/skills/)

| Skill | Capa del PATRÓN | Capa del CONTENIDO | Acción | Justificación |
|---|---|---|---|---|
| `cerrar-modulo-entrevoces` | **1** | 3 | GENERALIZAR → `cerrar-modulo` | Patrón universal: puerta de cierre → verificar evidencia → actualizar estado → log → siguiente paso. Funciona idéntico en cualquier proyecto con documentación viva |
| `evaluar-agente-entrevoces` | **1** | 3 | GENERALIZAR → `evaluar-agente` | Patrón universal de evaluación de agentes LLM: normal/ambiguo/adversarial/fallo + campos de registro + criterio de aprobación 100% rechazo en ataques |
| `probar-e2e-entrevoces` | **1** | 3 | GENERALIZAR → `probar-e2e` | Patrón universal de E2E: datos controlados → recorrido obligatorio → negativos → tabla de evidencia → veredicto APROBADO/NO_APROBADO |
| *(nueva)* `delegar-entre-agentes` | **1 opcional** | — | NO incluir por defecto | Aspiracional: no hay evidencia de uso real en EntreVoces (6 hitos sin handoffs formales). Incluir solo cuando PROJECT_STATE.md resulte insuficiente |
| `desarrollar-backend-entrevoces` | **2** | 3 | MOVER → `stacks/web-backend/desarrollar-backend` | Patrón específico de proyectos FastAPI/REST: contrato Pydantic → test → router→servicio→repo → límites de autoridad |
| `desarrollar-firmware-entrevoces` | **2** | 3 | MOVER → `stacks/firmware-esp32/desarrollar-firmware` | Patrón específico de MicroPython+ESP32: confirmar hw → prueba aislada → máquina de estados → PSRAM → bloques |
| `diagnosticar-hardware-entrevoces` | **2** | 3 | MOVER → `stacks/firmware-esp32/diagnosticar-hardware` | Patrón de diagnóstico hardware: secuencia ordenada → puertas de seguridad → registro de evidencia con estados |
| `validar-audio-dispositivo` | **2** | 3 | MOVER → `stacks/firmware-esp32/validar-audio` | Patrón de validación de audio embebido: preservar original → inspeccionar → separar capas de fallo → muestra controlada |

## Documentación (documentacion/)

| Archivo | Capa | Acción | Notas |
|---|---|---|---|
| `DOCUMENTACION_TECNICA.md` | 3 | MANTENER | 100% instancia: endpoints, tablas, contratos específicos de EntreVoces |
| `GUIA_BACKEND.md` | 3 | MANTENER | 100% instancia: comandos uv, variables ENTREVOCES_*, configuración |
| `GUIA_DISPOSITIVO_H3.md` | 3 | MANTENER | 100% instancia: archivos MicroPython, GPIO, prueba H3 |
| `GUIA_OPERACION_Y_ARQUITECTURA.md` | 2+3 | MANTENER | Formato (18 secciones) es Capa 2 para IoT+backend. Contenido es Capa 3 |
| `GUIA_SECRETOS_CLAUDE.md` | 1 | RENOMBRAR → `GUIA_SECRETOS.md` | Contenido genérico: protocolo de secretos, auditoría, checklist. Solo ejemplos nombran ENTREVOCES_ |
| `GUIA_SESIONES_ANTIGRAVITY.md` | 1+3 | GENERALIZAR | Protocolo (crear chat, auditar, probar skills, cerrar) es Capa 1. Plantillas nombran EntreVoces |
| `HERRAMIENTAS_DISPONIBLES_CLAUDE.md` | 1 | RENOMBRAR → `HERRAMIENTAS_AGENTE.md` | Describe capacidades/limitaciones genéricas de un agente no autónomo |
| `INDICE_DOCUMENTACION.md` | 1+3 | FUSIONAR dentro de INDICE_LECTURA | Lista plana es subconjunto del índice por tarea. Fusionar como sección final |
| `INDICE_LECTURA_CLAUDE.md` | 1+3 | RENOMBRAR → `INDICE_LECTURA_AGENTES.md` | Patrón (lectura por tipo de tarea, tokens, checklist) es Capa 1 reutilizable |
| `PLAN_DESARROLLO_MVP.md` | 2+3 | MANTENER (extraer formato) | Estructura de hitos con criterios de salida es Capa 2 para MVPs. Contenido H0-H8 es Capa 3 |
| `PLAN_DESARROLLO_SERVIDOR.md` | 3 | MANTENER | 100% instancia: 14 pasos específicos del servidor EntreVoces |
| `PROMPT_SISTEMA_CLAUDE.md` | 1+3 | FUSIONAR → base + delta | 80% duplicado con IA.md. Reducir a delta Claude |
| `PROMPT_SISTEMA_IA.md` | 1+3 | FUSIONAR → `SYSTEM_PROMPT_BASE.md` | Se convierte en la base unificada |
| `REGISTRO_CAMBIOS.md` | 1+3 | MANTENER (extraer formato) | Formato (cronológico, acumulativo, convenciones) es Capa 1. Entradas son Capa 3 |

## Entrega Antigravity (entrega_antigravity/)

| Archivo | Capa | Acción | Notas |
|---|---|---|---|
| `AGENTS.md` | 3 | SINCRONIZADO (Fase 1) | Ahora es copia exacta de raíz. Futuro: automatizar sync o usar symlink |
| `PROJECT_STATE.md` | 3 | SINCRONIZADO (Fase 1) | Ahora es copia exacta de raíz |
| `PROMPT_SISTEMA_ANTIGRAVITY.md` | 1+3 | REDUCIR → delta | En Fase 3, se convierte en referencia a base + delta mínimo |
| `README_INSTALACION.md` | 3 | MANTENER | Instrucciones específicas del paquete portable |
| `.agents/rules/entrevoces_mvp.md` | 3 | MANTENER | Regla always-on necesaria para workspace Antigravity |
| `.agents/skills/*` | 2+3 | MANTENER | Copia del paquete portable — ya usa `referencias/` (correcto) |

## Resumen cuantitativo

| Capa | Archivos analizados | Acción dominante |
|---|---|---|
| Capa 1 pura | 4 | GENERALIZAR |
| Capa 1+3 (mixtos) | 14 | GENERALIZAR o FUSIONAR |
| Capa 2+3 | 6 | MOVER a domain-pack |
| Capa 3 pura | 8 | MANTENER |
| Redundantes | 4 | ELIMINAR o FUSIONAR |
