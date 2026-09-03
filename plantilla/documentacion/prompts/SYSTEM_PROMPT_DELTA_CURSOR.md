# Delta para Cursor — {{NOMBRE_PROYECTO}}

**Aplica sobre:** `SYSTEM_PROMPT_BASE.md`
**Agente:** Cursor

---

## Descubrimiento del proyecto

Cursor usa `AGENTS.md` como regla del repositorio y descubre las Skills canonicas en
`.agents/skills/`. Se debe comprobar en la sesion que las reglas y Skills esperadas
aparezcan antes de asumir que fueron cargadas; las sesiones remotas solo reciben los
archivos versionados en el proyecto.

## Operacion

- Lee `PROJECT_STATE.md` antes de modificar codigo.
- Aplica solamente las Skills instaladas y pertinentes para la tarea.
- Respeta los permisos y herramientas observables de la sesion.
- Ejecuta la validacion indicada por `AGENTS.md` antes de cerrar el cambio.
