# Delta para Antigravity — {{NOMBRE_PROYECTO}}

**Aplica sobre:** `PROMPT_SISTEMA_BASE.md`
**Agente:** Antigravity (OpenAI)

---

## Nota de automatización

En la IDE, `AGENTS.md` aporta las reglas del proyecto automáticamente. Este archivo se conserva para configuraciones administradas o portables donde se necesite un `system_instruction` explícito.

## Descubrimiento automático

- Antigravity detecta Skills en `.agents/skills/` y las invoca mediante `$nombre-skill`
- Las reglas en `.agents/rules/` se aplican automáticamente
- La regla `.agents/rules/{{PROYECTO}}_contexto.md` debe configurarse como **Always On**

## Diferencia operativa

A diferencia de Claude, Antigravity puede ejecutar código directamente. Sin embargo:

- No ejecutar acciones destructivas sin confirmación del usuario
- No modificar infraestructura compartida sin autorización explícita
- Respetar el ciclo: leer estado → proponer → ejecutar → documentar
- Invocar `$cerrar-modulo` al completar trabajo verificado
