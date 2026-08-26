# Índice de lectura para agentes — {{NOMBRE_PROYECTO}}

## Lectura obligatoria (siempre, al inicio de sesión)

| # | Archivo | Propósito |
|---|---|---|
| 1 | `AGENTS.md` | Reglas permanentes del proyecto |
| 2 | `PROJECT_STATE.md` | Estado actual e hito vigente |

## Lectura según tarea

| Tarea | Archivos adicionales |
|---|---|
| Implementar backend | `.agents/skills/*/SKILL.md` relevante, `documentacion/prompts/PROMPT_SISTEMA_BASE.md` |
| Depurar problema | `documentacion/REGISTRO_CAMBIOS.md` (cambios recientes), logs en `infraestructura/registros/` |
| Cerrar módulo | `.agents/skills/cerrar-modulo/SKILL.md` |
| Evaluar calidad | `.agents/skills/evaluar-agente/SKILL.md` + `referencias/casos_evaluacion.md` |
| Handoff a otro agente | `.agents/skills/delegar-entre-agentes/SKILL.md` |

## NO leer salvo que se necesite

- Archivos de infraestructura/configuración (docker, CI) — solo si la tarea lo requiere
- Logs históricos completos — usar `git log` en su lugar
- Código fuente completo — pedir contexto específico al usuario

## Convención

Cuando un agente necesita contexto que no tiene, debe solicitar archivos específicos por ruta, no "todo el proyecto".
