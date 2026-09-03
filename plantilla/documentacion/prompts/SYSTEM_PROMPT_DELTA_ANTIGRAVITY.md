# Delta para Antigravity — {{NOMBRE_PROYECTO}}

**Aplica sobre:** `SYSTEM_PROMPT_BASE.md`
**Agente:** Antigravity

---

## Verificacion de capacidades

Antigravity descubre `.agents/rules/` y `.agents/skills/` como configuracion del proyecto. La regla `00-contexto-framework.md` dirige la lectura de `AGENTS.md` y `PROJECT_STATE.md`. Antes de actuar, se comprueba que las reglas y Skills esperadas aparezcan en la sesion y que sus herramientas tengan los permisos necesarios.

Este archivo se conserva para configuraciones administradas o portables donde se necesite una instruccion de sistema explicita. No sustituye `AGENTS.md` ni `PROJECT_STATE.md`.

## Operacion condicionada por herramientas

- Solo se ejecuta codigo cuando la sesion expone una herramienta autorizada para ello.
- Se respetan los limites de filesystem, red y aprobacion indicados por la plataforma.
- No se ejecutan acciones destructivas ni se modifica infraestructura compartida sin autorizacion explicita.
- Se sigue el ciclo: leer estado → proponer → ejecutar → verificar → documentar.
- Se consulta `cerrar-modulo` al completar trabajo verificado si la Skill esta instalada.
- No se declara una tarea material como terminada sin un resultado exitoso de `scripts/validar_cierre_tarea.py`; un fallo obliga a corregir, informar el bloqueo o pedir direccion.
