---
name: delegar-entre-agentes
description: "OPCIONAL — Formaliza el traspaso de trabajo entre agentes distintos (Claude, Antigravity, Codex u otros) sobre el mismo proyecto. Usar cuando se cambia de herramienta entre sesiones y hay decisiones activas, razonamiento en curso o contexto que PROJECT_STATE.md §8 no alcanza a capturar. No usar para handoffs simples donde basta actualizar PROJECT_STATE.md."
---

# Delegar entre agentes

## Para que sirve

Cuando se trabaja en un proyecto con varios agentes — por ejemplo, Claude en VS Code para analisis profundo, Antigravity con Gemini para ejecucion rapida en el IDE, y Codex para tareas autonomas en background — el traspaso necesita mas que un "siguiente paso" en PROJECT_STATE.md.

Esta Skill formaliza ese traspaso para que el agente receptor pueda continuar sin perdida de contexto significativa.

## Cuando usar

- Se cambia de herramienta por preferencia, disponibilidad o porque la tarea se beneficia de las fortalezas de otro agente.
- Hay razonamiento en curso, decisiones a medias o contexto de sesion que no cabe en PROJECT_STATE.md §8.
- Se agoto el contexto del agente actual en medio de una tarea compleja.
- La tarea requiere capacidades especificas de otro agente (descubrimiento automatico, ejecucion autonoma, contexto largo).

## Cuando NO usar

Si el cambio es simple y PROJECT_STATE.md §8 ya tiene el siguiente paso claro, no hace falta esta Skill. Basta con actualizar PROJECT_STATE.md y abrir la nueva sesion con el template del README §5.

## Protocolo de entrega

El agente que termina la sesion debe:

1. **Cerrar hasta donde se verifico.** No dejar archivos modificados sin commit ni trabajo a medias sin tests ni documentacion.
2. **Actualizar `PROJECT_STATE.md`** con estado exacto — no "en progreso", sino que esta hecho y que falta.
3. **Escribir en `documentacion/REGISTRO_CAMBIOS.md`** que se avanzo en esta sesion.
4. **Documentar el traspaso en `PROJECT_STATE.md` §8** con:
   - agente que entrega y motivo del cambio;
   - agente destino recomendado y por que;
   - tarea concreta pendiente (1 oracion imperativa);
   - archivos relevantes (maximo 5 rutas);
   - decisiones abiertas que el usuario debe tomar antes de continuar;
   - bloqueos conocidos que el siguiente agente encontrara.
5. **Hacer commit** con un mensaje descriptivo del avance.

### Template rapido de traspaso

El agente puede generar este bloque al final de la sesion para facilitar la continuidad:

```
## Traspaso de sesion

**Agente saliente:** [nombre y herramienta]
**Motivo del cambio:** [limite de contexto / preferencia / tarea especifica]
**Agente recomendado:** [nombre y por que]

### Estado al cerrar
- Ultimo cambio: [que se hizo]
- Tests: [pasan / fallan / pendientes]
- Commit: [hash o pendiente]

### Pendiente inmediato
[1 oracion imperativa: "Implementar X en Y usando Z"]

### Archivos clave
1. [ruta]
2. [ruta]

### Decisiones abiertas
- [decision que el usuario debe tomar]

### Bloqueos
- [bloqueo conocido, o "ninguno"]
```

## Lo que NO es un handoff valido

- Pedir "termina esto" sin contexto de que "esto" incluye.
- Duplicar el trabajo del otro agente por no leer PROJECT_STATE.md.
- Cambiar de agente por frustracion sin diagnosticar el problema real.
- Dejar archivos modificados sin commit ni registro.
- Asumir que el agente anterior hizo todo correctamente sin verificar.

## Protocolo de recepcion

El agente que recibe debe:

1. Leer `AGENTS.md` y `PROJECT_STATE.md` (como siempre).
2. Verificar §8 para entender que se espera y si hay un traspaso documentado.
3. Confirmar con el usuario si hay decisiones pendientes documentadas.
4. NO asumir que el trabajo previo esta correcto — verificar con tests o inspeccion antes de continuar.
5. Si encuentra inconsistencias entre el estado documentado y el estado real, reportar antes de actuar.

## Agentes conocidos y sus fortalezas

| Agente | Fortaleza principal | Cuando elegirlo |
|---|---|---|
| Claude (VS Code / Claude Code) | Contexto largo, analisis profundo, edicion iterativa con aprobacion | Tareas de analisis, refactorizacion compleja, revision de arquitectura |
| Antigravity (Gemini) | Descubrimiento automatico de Skills y rules, ejecucion directa en IDE | Desarrollo rapido, tareas que usan Skills del proyecto, flujos de implementacion |
| Codex CLI | Ejecucion autonoma en background sin supervision continua | Tareas bien definidas que pueden correr solas: tests, migraciones, generacion de codigo repetitivo |

Esta tabla es orientativa. Las capacidades reales dependen de la version y configuracion de cada herramienta. El agente debe comprobar sus herramientas y permisos observables, no asumir capacidades por marca.
