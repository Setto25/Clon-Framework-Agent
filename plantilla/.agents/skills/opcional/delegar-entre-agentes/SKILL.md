---
name: delegar-entre-agentes
description: "OPCIONAL — Prepara un handoff entre agentes (Claude Code/Antigravity/Codex) documentando contexto, decisiones pendientes y siguiente acción concreta. Usar cuando se detecte que la continuidad vía PROJECT_STATE.md no es suficiente (pérdida de contexto entre sesiones, decisiones que se repiten). No incluir en proyectos nuevos hasta que el problema se manifieste."
---

# Delegar entre agentes

## Cuándo delegar

- El contexto actual está saturado y se necesita sesión fresca con estado limpio.
- La tarea se beneficia del descubrimiento automático de Skills (→ Antigravity).
- Se necesita ejecución autónoma en background sin supervisión (→ Codex).
- Se necesita análisis profundo con contexto largo y edición iterativa (→ Claude Code).
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
