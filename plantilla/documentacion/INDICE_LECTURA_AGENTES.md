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
| Implementar en un stack especifico | `stacks/<stack>/LEEME.md`, reglas del stack |
| Nombres de variables/funciones | `.agents/rules/excepciones_nominales.md` |
| Depurar error no trivial | `.agents/skills/lecciones-aprendidas/referencias/<stack>.md` |
| Cerrar modulo | `.agents/skills/cerrar-modulo/SKILL.md` |
| Evaluar calidad | `.agents/skills/evaluar-agente/SKILL.md` |
| Iniciar proyecto nuevo | `.agents/skills/iniciar-proyecto/SKILL.md` |
| Handoff a otro agente | `opcional/delegar-entre-agentes/SKILL.md` — usar solo si `PROJECT_STATE.md §8` no alcanza para que el agente siguiente retome (razonamiento en curso, decision a medias). En la practica rara vez se necesita. |

## NO leer por defecto

- `documentacion/analisis/` — Solo si se necesita contexto historico de la extraccion del framework.
- `documentacion/REGISTRO_CAMBIOS.md` completo — Usar `git log` o leer solo las ultimas 5-10 entradas.
- Codigo fuente completo — Solicitar archivos especificos por ruta.
- Archivos de infraestructura (docker, CI) — Solo si la tarea lo requiere.

## Nota sobre Skills

Los skills NO se listan exhaustivamente aqui. Cada skill tiene su propio mecanismo de descubrimiento via metadata en `SKILL.md` (campo `name` + `description` en frontmatter). El agente consulta el skill relevante cuando la tarea coincide con su descripcion.

## Convencion

Cuando un agente necesita contexto que no tiene, debe solicitar archivos especificos por ruta, no "todo el proyecto".
