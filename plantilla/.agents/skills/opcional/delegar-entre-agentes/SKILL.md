---
name: delegar-entre-agentes
description: "OPCIONAL — Sin evidencia de uso real (extraido de entrevoces, 6 hitos sin handoffs formales). Usar cuando el limite de contexto dentro de una sesion hace que el agente pierda decisiones importantes que PROJECT_STATE.md no captura — por ejemplo, un razonamiento en curso o una decision a medias. En la practica, PROJECT_STATE.md suele ser suficiente para el handoff entre sesiones, asi que este skill rara vez se necesita. No activar por defecto en proyectos nuevos."
---

# Delegar entre agentes

> **Skill opcional — rara vez necesario.** Antes de usarlo, verifica que `PROJECT_STATE.md §8` (Siguiente paso logico) este completo. En la mayoria de los casos eso es suficiente para que un agente nuevo retome sin perdida. Usa este skill solo si hay razonamiento en curso o decisiones a medias que no caben en PROJECT_STATE.md.

## Cuando delegar

- El contexto del agente se agoto en medio de una tarea compleja y hay decisiones activas que PROJECT_STATE.md no puede capturar en su formato.
- La tarea se beneficia del descubrimiento automatico de Skills (→ Antigravity).
- Se necesita ejecucion autonoma en background sin supervision (→ Codex).
- Se necesita analisis profundo con contexto largo y edicion iterativa (→ Claude Code).
- El usuario cambia de herramienta por preferencia o disponibilidad.

## Protocolo de handoff

1. Actualizar `PROJECT_STATE.md` con estado exacto (no "en progreso" — qué está hecho y qué falta).
2. Escribir en `documentacion/REGISTRO_CAMBIOS.md` qué se avanzó en esta sesión.
3. Documentar en `PROJECT_STATE.md` §8 (Siguiente paso lógico):
   - Agente que entrega y motivo del handoff.
   - Agente destino recomendado y por qué.
   - Tarea concreta pendiente (1 oración imperativa).
   - Archivos relevantes (máximo 5 rutas).
   - Decisión que el usuario debe tomar antes de continuar (si aplica).
   - Bloqueos conocidos que el siguiente agente encontrará.
4. NO dejar trabajo a medias sin tests ni documentación — cerrar hasta donde se verificó.

## Lo que NO es un handoff válido

- Pedir "termina esto" sin contexto de qué "esto" incluye.
- Duplicar el trabajo del otro agente por no leer `PROJECT_STATE.md`.
- Cambiar de agente por frustración sin diagnosticar el problema real.
- Dejar archivos modificados sin commit ni registro.

## Recepción del handoff

El agente que recibe debe:

1. Leer `AGENTS.md` y `PROJECT_STATE.md` (como siempre).
2. Verificar §8 para entender qué se espera.
3. Confirmar con el usuario si hay decisiones pendientes documentadas.
4. NO asumir que el trabajo previo está correcto — verificar con tests o inspección.

## Agentes conocidos y sus fortalezas

| Agente | Ejecuta código | Fortaleza | Limitación principal |
|---|---|---|---|
| Claude Code | Sí (bash, edición, tests, git) | Contexto largo, análisis profundo, edición iterativa con aprobación del usuario | Requiere aprobación para acciones riesgosas; contexto se comprime en sesiones largas |
| Antigravity | Sí (ejecución directa en IDE) | Descubrimiento automático de Skills (`$nombre`), rules always-on | Contexto limitado por sesión; atado al IDE |
| Codex CLI | Sí (terminal autónoma) | Ejecución autónoma en background, sin supervisión continua | No descubre Skills automáticamente; contexto aislado por invocación |
