# Reglas de Claude en {{NOMBRE_PROYECTO}}

**Versión:** 2.0
**Agente:** Claude (Anthropic)

Estas reglas complementan `AGENTS.md`. Son aditivas — no reemplazan ninguna sección de AGENTS.md.

---

## 1. Lectura inicial obligatoria

Antes de cualquier tarea, Claude lee en este orden:

1. `AGENTS.md` — Reglas permanentes
2. `PROJECT_STATE.md` — Estado actual
3. `documentacion/INDICE_LECTURA_AGENTES.md` — Guía de contexto por tipo de tarea
4. Documentación específica de la tarea

Claude comunica qué leyó antes de actuar.

---

## 2. Ciclo de trabajo

1. **Explorar**: Entender estado actual, restricciones y trabajo previo
2. **Proponer**: 2-3 enfoques con tradeoffs concretos, recomendar uno
3. **Planificar**: Tras aprobación del usuario, detallar pasos y tests esperados
4. **Implementar (TDD)**: Escribir test que falla → implementar mínimo → refactorizar
5. **Verificar**: Ejecutar suite, revisar código contra checklist §4, comprobar AGENTS.md
6. **Cerrar**: `$cerrar-modulo` si el módulo está completo; si no, documentar estado parcial

Claude NUNCA asume que puede ejecutar código directamente. Proporciona comandos que el usuario ejecuta e interpreta resultados para iterar.

---

## 3. Depuración sistemática

Cuando algo falla:

1. **Reproducir**: Obtener el error exacto con pasos mínimos y entrada conocida
2. **Aislar**: Determinar componente responsable (búsqueda binaria entre capas)
3. **Hipótesis**: Formular 1-2 causas probables y diseñar experimento mínimo que las distinga
4. **Verificar fix**: El test que reproducía el fallo ahora pasa; la suite completa no regresiona

No adivinar. No cambiar múltiples cosas a la vez. No asumir la causa sin evidencia.

---

## 4. Revisión de código

Antes de entregar código final:

- [ ] **Corrección lógica**: edge cases, off-by-one, null handling, concurrencia
- [ ] **Seguridad**: secretos, injection, autoridad, OWASP top 10
- [ ] **Rendimiento**: N+1, buffers sin límite, timeouts ausentes, queries sin índice
- [ ] **Estilo**: cumple AGENTS.md §1 (idioma, tipado, docstrings, naming)
- [ ] **Pruebas**: cubren el caso nuevo y no introducen regresiones conocidas
- [ ] **Sin secretos**: ni en código, ni en logs, ni en respuestas, ni en comentarios

---

## 5. Gestión de contexto

- Solicitar solo contexto necesario para la tarea actual (archivos, secciones)
- Reutilizar contexto entre iteraciones de la misma tarea
- Comunicar cuando el contexto resulte insuficiente para tomar una decisión
- No pedir "todo el proyecto" — pedir secciones específicas

---

## 6. Seguridad de secretos

**NUNCA incluir secretos en prompts, código o documentación.**

1. Detectar dónde se necesitan credenciales
2. Documentar el nombre de la variable requerida
3. Instruir cómo configurar en `.env`
4. Usar `os.getenv("{{PREFIJO_VARIABLES}}_NOMBRE_SECRETO")`
5. Nunca repetir el valor en prompts, código ni salida

---

## 7. Consulta de Skills

Cuando una tarea coincida con una Skill:

1. Comunicar: "Voy a consultar la Skill [nombre]"
2. Leer completamente el `SKILL.md` y sus referencias
3. Seguir el protocolo paso a paso
4. Adaptar al contexto actual del proyecto

---

## 8. Comunicación

Comunicar primero el resultado, luego la evidencia, luego los riesgos:

```
COMPLETADO: [qué se hizo en 1 línea]

Qué se hizo:
- [detalle 1]
- [detalle 2]

Evidencia:
- [pruebas, comandos ejecutados]

Riesgo: [si aplica]
Siguiente: [paso lógico]
```

Cuando una decisión no bloquea, adoptar la opción más simple y reversible.

---

## 9. Compatibilidad con otros agentes

Estas reglas son compatibles con Antigravity, Codex y otros agentes que usen `AGENTS.md` como base. Las secciones de arquitectura, idioma y autoridad se aplican vía `AGENTS.md` directamente — no se duplican aquí.
