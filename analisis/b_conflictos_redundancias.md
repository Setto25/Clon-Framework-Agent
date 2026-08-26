# (b) Lista completa de conflictos y redundancias

**Fecha del análisis:** 2026-08-26
**Proyecto:** EntreVoces

---

## CONFLICTOS DE DIVERGENCIA

### C1. AGENTS.md raíz vs entrega_antigravity/AGENTS.md

**Estado:** RESUELTO en Fase 1 (sincronizado el 2026-08-26)

| Aspecto | Raíz (fuente de verdad) | entrega_antigravity (antes de fix) |
|---|---|---|
| Líneas | 105 | 64 |
| §1 excepciones | `.env`, `.env.ejemplo`, `conftest.py`, `agents/openai.yaml` | Solo `main.py`, `diagram.json`, `pyproject.toml`, `uv.lock`, `.python-version`, `.venv` |
| §2 Memoria | Incluye GUIA_OPERACION (líneas 28-31) | No la menciona |
| §7 Multi-agente | EXISTE (líneas 69-104) | NO EXISTE |

**Cita exacta de la divergencia principal:**
- Raíz línea 7: `AGENTS.md`, `PROJECT_STATE.md`, `.agents/skills`, `SKILL.md`, `agents/openai.yaml`, `main.py`, `diagram.json`, `pyproject.toml`, `uv.lock`, `.python-version`, `.venv`, `.env`, `.env.ejemplo` y `conftest.py`
- Entrega línea 7 (antes): `AGENTS.md`, `PROJECT_STATE.md`, `.agents/skills`, `.agents/rules`, `SKILL.md`, `main.py`, `diagram.json`, `pyproject.toml`, `uv.lock`, `.python-version` y `.venv`

---

### C2. PROJECT_STATE.md raíz vs entrega_antigravity/PROJECT_STATE.md

**Estado:** RESUELTO en Fase 1 (sincronizado el 2026-08-26)

| Aspecto | Raíz | entrega_antigravity (antes de fix) |
|---|---|---|
| Última actualización | 2026-08-22 | 2026-08-18 |
| Fase activa | H6 (Cliente público) | H2 (Validación hardware) |
| Secciones | 13 | 10 |
| §3 Hardware | Mapa completo GPIO con pines verificados | Solo lista sin pines |
| §4 Decisiones | 18 | 16 |
| §6 Implementado | H1 completo + H2 + H3 + H4 + H5 | Solo hasta inicio H2 |
| §7 Tecnologías | pgvector, Sentence Transformers, PyTorch, Gemini | Solo FastAPI/uv básico |
| §11-13 | Infraestructura, gobernanza, .env | NO EXISTEN |

**Impacto:** Antigravity con la copia vieja creía que el proyecto estaba en H2, ignorando 6 hitos de trabajo completado.

---

### C3. Skill `cerrar-modulo-entrevoces` raíz vs entrega_antigravity

**Estado:** PENDIENTE (diferencia menor, no crítica)

- **Raíz** (`.agents/skills/cerrar-modulo-entrevoces/SKILL.md` §Actualización obligatoria punto 5):
  ```
  5. Revisar `documentacion/GUIA_OPERACION_Y_ARQUITECTURA.md`; actualizarla cuando el cambio altere operación...
  6. Ejecutar `scripts/verificar_memoria_proyecto.py` desde esta Skill.
  ```
- **Entrega** (`.agents/skills/cerrar-modulo-entrevoces/SKILL.md` §Actualización obligatoria):
  ```
  5. Ejecutar `scripts/verificar_memoria_proyecto.py` desde esta Skill.
  ```
  (Falta el paso de revisar GUIA_OPERACION)

**Archivo:** `entrega_antigravity/.agents/skills/cerrar-modulo-entrevoces/SKILL.md`, §Actualización obligatoria
**Cita:** Ausencia del punto 5 sobre GUIA_OPERACION entre puntos 4 y 5(actual)

---

### C4. Carpetas `references/` vs `referencias/`

**Estado:** RESUELTO en Fase 1

- **Raíz skills:** Usaban `references/` (inglés) — violaba AGENTS.md §1
- **Entrega skills:** Usaban `referencias/` (español) — correcto
- **SKILL.md de ambos:** Referenciaban `referencias/` (español)

**Resultado:** Los links internos de los SKILL.md de raíz estaban ROTOS hasta el fix.

---

## REDUNDANCIAS

### R1. `PROMPT_SISTEMA_IA.md` vs `PROMPT_SISTEMA_CLAUDE.md`

**Estado:** PENDIENTE (Fase 3)

**Archivos:**
- `documentacion/PROMPT_SISTEMA_IA.md` (250 líneas, v1.1, 2026-08-22)
- `documentacion/PROMPT_SISTEMA_CLAUDE.md` (236 líneas, v1.0, 2026-08-24)

**Solapamiento:** ~80% de contenido idéntico.

**Secciones duplicadas (presentes en ambos):**
| Sección | En IA.md | En CLAUDE.md |
|---|---|---|
| Rol y objetivo | §intro | §Rol y objetivo |
| Jerarquía y lectura inicial | §Jerarquía | §Jerarquía |
| Prioridad del MVP | §Prioridad | §Prioridad |
| Reglas de idioma y tipado | §Reglas estrictas | §Reglas estrictas |
| Arquitectura obligatoria | §Arquitectura | §Arquitectura |
| Autoridad limitada | §Regla de autoridad | §Regla de autoridad |
| Proveedores desacoplados | §Proveedores | §Proveedores |
| Moderación | §Reglas de contenido | §Reglas de contenido |
| Búsqueda semántica | §Búsqueda | §Búsqueda |
| Contrato de audio | §Contrato | §Contrato |
| Hardware | §Condiciones | §Condiciones |
| Implementación | §Forma | §Forma |
| Terminado | §Definición | §Definición |
| Memoria | §Actualización | §Actualización |
| Comunicación | §Comunicación | §Comunicación |

**Contenido SOLO en CLAUDE.md (el delta real):**
- "Claude NO es autónomo" (§Limitaciones, línea ~139)
- "Proporciona comandos que el usuario ejecuta" (§Modo colaborativo)
- Solicitud de contexto explícita con template (§Gestión de contexto)

---

### R2. `INDICE_DOCUMENTACION.md` vs `INDICE_LECTURA_CLAUDE.md`

**Estado:** PENDIENTE (Fase 2)

**Archivos:**
- `documentacion/INDICE_DOCUMENTACION.md` (72 líneas → 80 tras fix, v0.4)
- `documentacion/INDICE_LECTURA_CLAUDE.md` (261 líneas, v1.0, 2026-08-24)

**Relación:** El primero es un subconjunto pobre del segundo.
- INDICE_DOCUMENTACION: lista plana de 13 archivos + regla de sesión/cierre
- INDICE_LECTURA_CLAUDE: lo mismo PLUS lectura por tipo de tarea, optimización de tokens, checklist, tabla de referencia por archivo

**Contenido único de INDICE_DOCUMENTACION (a preservar en fusión):**
- Sección "Regla de uso al comenzar una sesión" (líneas 52-61)
- Sección "Regla de cierre de una sesión" (líneas 63-71)

---

### R3. `.agents/rules/entrevoces_mvp.md` (raíz) vs `AGENTS.md` §1-§5

**Estado:** RESUELTO en Fase 1 (eliminado)

**Archivos:**
- `.agents/rules/entrevoces_mvp.md` (34 líneas) — ELIMINADO
- `AGENTS.md` §1-§5 (58 líneas)

**Solapamiento:** 100%. La regla era una compresión literal de:
- §Inicio obligatorio = AGENTS.md §2 (lectura de PROJECT_STATE antes de actuar)
- §Invariantes = AGENTS.md §1 (español) + §3 (arquitectura)
- §Prioridad y cierre = AGENTS.md §4 + §5

**Motivo de eliminación:** Antigravity ya lee AGENTS.md automáticamente al detectarlo en la raíz.

---

### R4. `rules/claude.md` §6-8 vs `AGENTS.md` §1, §3

**Estado:** PENDIENTE (Fase 4)

**Archivos:**
- `.agents/rules/claude.md` §6 "Estilo de código" (líneas 121-143)
- `.agents/rules/claude.md` §7 "Arquitectura obligatoria" (líneas 146-160)
- `.agents/rules/claude.md` §8 "Autoridad limitada" (líneas 163-180)
- `AGENTS.md` §1 "Estilo de código" (líneas 3-19)
- `AGENTS.md` §3 "Arquitectura y seguridad" (líneas 33-40)

**Solapamiento:** Verbatim. Las secciones de rules/claude.md repiten exactamente las mismas reglas con formato ligeramente diferente.

**Cita exacta de duplicación:**
- rules/claude.md línea 125: "Nombres: Español obligatorio (archivos, módulos, clases, funciones)"
- AGENTS.md línea 5: "Todos los nombres creados para archivos, carpetas, módulos, clases, esquemas, modelos y routers deben escribirse obligatoriamente en español."
- rules/claude.md línea 155: "ESP32 y Flutter NUNCA acceden directamente a PostgreSQL"
- AGENTS.md línea 34: "Los clientes no deben acceder directamente a PostgreSQL."

---

### R5. `rules/claude.md` §9-10 vs Skill `cerrar-modulo-entrevoces`

**Estado:** PENDIENTE (Fase 4)

**Archivos:**
- `.agents/rules/claude.md` §9 "Definición de terminado" (líneas 186-199)
- `.agents/rules/claude.md` §10 "Actualización de memoria" (líneas 201-220)
- `.agents/skills/cerrar-modulo-entrevoces/SKILL.md` §Puerta de cierre + §Actualización obligatoria

**Solapamiento:** La regla y la Skill dicen lo mismo. La Skill agrega el script de verificación; la regla agrega el formato de comunicación.

---

### R6. `PROMPT_SISTEMA_ANTIGRAVITY.md` §Hardware vs realidad actual

**Estado:** PENDIENTE (Fase 3)

**Archivo:** `entrega_antigravity/PROMPT_SISTEMA_ANTIGRAVITY.md`, §Condiciones del hardware (líneas 179-193)

**Desactualización:**
- Línea 179: "pantalla ST7789V 240×320 por SPI, **PCM5102A por I2S**, PAM8403"
- Realidad (PROJECT_STATE.md §4 decisión 17): "descartando el uso de la placa DAC intermedia silenciada de fábrica"
- Línea 187: "Prueba PCM5102A antes de agregar PAM8403"
- Realidad: PWM directo D1→PAM8403 sin DAC intermedio

**Impacto:** Antigravity puede sugerir probar el PCM5102A que ya fue descartado.

---

## DESACTUALIZACIONES

### D1. `INDICE_DOCUMENTACION.md` v0.3 (2026-08-21)

**Estado:** RESUELTO en Fase 1 (actualizado a v0.4)

Faltaban:
- `GUIA_SECRETOS_CLAUDE.md` (creado 2026-08-24)
- `INDICE_LECTURA_CLAUDE.md` (creado 2026-08-24)
- `HERRAMIENTAS_DISPONIBLES_CLAUDE.md` (creado 2026-08-24)

---

### D2. `DOCUMENTACION_TECNICA.md` v1.8 (2026-08-21)

**Estado:** PENDIENTE (menor)

**Archivo:** `documentacion/DOCUMENTACION_TECNICA.md`
**Falta:** Referencia a la configuración .env implementada el 2026-08-22 (§13 de PROJECT_STATE). La sección §0.1 "Entorno y verificación" no menciona `python-dotenv` ni `configuracion_entorno.py`.

---

### D3. `PROMPT_SISTEMA_ANTIGRAVITY.md` v1.1 (2026-08-18)

**Estado:** PENDIENTE (Fase 3 lo eliminará)

**Desactualización:** §Hardware menciona PCM5102A como componente activo (descartado en H2.6, 2026-08-21).

---

## SOLAPAMIENTO CON SUPERPOWERS

### S1. Planificación

**Estado:** PENDIENTE (Fase 4)

| Concepto | En `rules/claude.md` §2 | En superpowers |
|---|---|---|
| Plan antes de codear | "Claude propone plan (PLAN MODE)" línea 31 | Brainstorming → Plan → Aprobación |
| Aprobación | "Usuario aprueba o ajusta" línea 32 | Mismo concepto |
| Ejecución | "Claude ejecuta (ACT MODE)" línea 33 | Implementación |

**Veredicto:** Solapamiento DIRECTO. §2 se reemplaza por ciclo superpowers más completo.

---

### S2. Depuración

| Concepto | En `rules/claude.md` §13 | En superpowers |
|---|---|---|
| Analizar error | "Lee completamente el mensaje" línea 285 | Reproducir |
| Identificar causa | "Propone hipótesis" línea 286 | Aislar + Hipótesis |
| Solución | "Código o pasos específicos" línea 287 | Verificar fix |
| Verificar | "Solicita que ejecute" línea 288 | Verificar fix |

**Veredicto:** Solapamiento PARCIAL. §13 es más superficial. Se reemplaza por las 4 fases sistemáticas.

---

### S3. Revisión de código

| Concepto | En `rules/claude.md` §15 | En superpowers |
|---|---|---|
| Correctness | "Que el código sea correcto" línea 306 | Correctness |
| Reglas | "Que siga reglas de AGENTS.md" línea 307 | Style |
| Tipado | "Que tenga type hints" línea 308 | Style |
| Secretos | "Que no incluya secretos" línea 309 | Security |
| Reproducible | "Que sea reproducible" línea 310 | — |
| Performance | — | Performance |
| Tests | — | Test coverage |

**Veredicto:** Solapamiento PARCIAL. §15 cubre 5/6 checks pero falta Performance y Tests como dimensiones explícitas. Se expande.

---

## RESUMEN DE ESTADO

| ID | Tipo | Severidad | Estado |
|---|---|---|---|
| C1 | Divergencia | CRÍTICA | RESUELTO |
| C2 | Divergencia | CRÍTICA | RESUELTO |
| C3 | Divergencia | BAJA | PENDIENTE |
| C4 | Inconsistencia | MEDIA | RESUELTO |
| R1 | Redundancia | ALTA | PENDIENTE (Fase 3) |
| R2 | Redundancia | MEDIA | PENDIENTE (Fase 2) |
| R3 | Redundancia | MEDIA | RESUELTO |
| R4 | Redundancia | MEDIA | PENDIENTE (Fase 4) |
| R5 | Redundancia | BAJA | PENDIENTE (Fase 4) |
| R6 | Desactualización | MEDIA | PENDIENTE (Fase 3) |
| D1 | Desactualización | BAJA | RESUELTO |
| D2 | Desactualización | BAJA | PENDIENTE |
| D3 | Desactualización | MEDIA | PENDIENTE (Fase 3) |
| S1 | Solapamiento | MEDIA | PENDIENTE (Fase 4) |
| S2 | Solapamiento | MEDIA | PENDIENTE (Fase 4) |
| S3 | Solapamiento | BAJA | PENDIENTE (Fase 4) |
