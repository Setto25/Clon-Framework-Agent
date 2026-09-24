# Indice de lectura para agentes — {{NOMBRE_PROYECTO}}

Claude Code recibe este mapa mediante `CLAUDE.md`; sus Skills visibles en
`.claude/skills/` remiten a las mismas fuentes canonicas enumeradas abajo.
opencode descubre esas fuentes canonicas mediante `skills.paths` en `opencode.json`.

## Lectura obligatoria (siempre, al inicio de sesion)

| # | Archivo | Proposito |
|---|---|---|
| 1 | `AGENTS.md` | Reglas permanentes del proyecto |
| 2 | `PROJECT_STATE.md` | Estado actual e hito vigente |
| 3 | `.agents/rules/claude.md` | Disciplina de proceso, eficiencia, lecciones aprendidas |

## Lectura condicional (segun tarea)

| Condicion | Archivos |
|---|---|
| Implementar en un stack instalado | `.agents/skills/stacks/<stack>/LEEME.md`, reglas del stack |
| Nombres de variables/funciones | `.agents/rules/excepciones_nominales.md` |
| Depurar error no trivial | `.agents/skills/lecciones-aprendidas/referencias/<stack>.md` |
| Cerrar modulo | `.agents/skills/cerrar-modulo/SKILL.md` |
| Evaluar un agente, si la Skill esta instalada | `.agents/skills/evaluar-agente/SKILL.md` |
| Crear otro proyecto, si la Skill esta instalada | `.agents/skills/iniciar-proyecto/SKILL.md` |
| Rutas desconocidas o exploracion repetida | `.agents/skills/optimizar-contexto/SKILL.md`; un indice fresco sustituye el listado inicial y sus referencias solo se leen al escalar |
| Cambio de agente, si la Skill opcional esta instalada | `.agents/skills/delegar-entre-agentes/SKILL.md` — protocolo de traspaso entre agentes distintos. |

## NO leer por defecto

- `documentacion/REGISTRO_CAMBIOS.md` completo — Usar `git log` o leer solo las ultimas 5-10 entradas.
- Codigo fuente completo — Solicitar archivos especificos por ruta.
- Archivos de infraestructura (docker, CI) — Solo si la tarea lo requiere.

## Nota sobre Skills

Solo se consideran disponibles los `SKILL.md` presentes en la instancia. El creador instala el core automatico y las Skills adicionales confirmadas. Cada Skill se descubre mediante `name` y `description` en su frontmatter.

## Convencion

Cuando un agente necesita contexto que no tiene, debe solicitar archivos especificos por ruta, no "todo el proyecto".
