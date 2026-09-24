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
- Antes de actualizar documentos de cierre se ejecuta `scripts/validar_cierre_tarea.py . --solo-verificaciones`; solo un codigo cero habilita esa actualizacion. Luego se ejecuta la puerta completa y se conserva su evidencia. Un fallo, ausencia de cobertura o herramienta obligatoria no disponible obliga a corregir, informar el bloqueo o pedir direccion.
- Un fallo de `lint` o `build` se corrige sin quitar su script de `package.json` ni su entrada del contrato. La puerta de integridad comprueba estos minimos para Next.js y la documentacion de cada cambio de codigo.
