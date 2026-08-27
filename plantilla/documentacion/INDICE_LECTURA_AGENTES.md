# Indice de lectura para agentes — {{NOMBRE_PROYECTO}}

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
| Handoff, si la Skill opcional esta instalada | `.agents/skills/delegar-entre-agentes/SKILL.md` — usar solo si `PROJECT_STATE.md §8` no alcanza para retomar. |

## NO leer por defecto

- `documentacion/analisis/` — Solo si se necesita contexto historico de la extraccion del framework.
- `documentacion/REGISTRO_CAMBIOS.md` completo — Usar `git log` o leer solo las ultimas 5-10 entradas.
- Codigo fuente completo — Solicitar archivos especificos por ruta.
- Archivos de infraestructura (docker, CI) — Solo si la tarea lo requiere.

## Nota sobre Skills

Solo se consideran disponibles los `SKILL.md` presentes en la instancia. El creador instala el core automatico y las Skills adicionales confirmadas. Cada Skill se descubre mediante `name` y `description` en su frontmatter.

## Convencion

Cuando un agente necesita contexto que no tiene, debe solicitar archivos especificos por ruta, no "todo el proyecto".
