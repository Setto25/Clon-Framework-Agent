# Reglas de Claude en {{NOMBRE_PROYECTO}}

**Versión:** 3.0
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

## 2. Disciplina de proceso (basado en superpowers)

### Brainstorming estructurado

Antes de planificar, generar 2-3 enfoques independientes:

1. **Declarar constraints**: listar las restricciones que cualquier solucion debe cumplir (ej: "no romper API publica", "funcionar sin migracion de datos", "completable en 1 sesion").
2. **Generar enfoques**: para cada uno, describir en 2-3 lineas qué hace diferente y qué sacrifica.
3. **Evaluar contra constraints**: marcar cual cumple todos, cual requiere excepciones.
4. **Recomendar uno**: con razon concreta. Documentar por qué se descartaron los otros (no solo "es mas simple" — qué riesgo o costo evita).

No es obligatorio para tareas triviales (< 20 lineas de cambio, sin decisiones arquitectonicas).

### Ciclo de trabajo (TDD red-green-refactor)

1. **Explorar**: Entender estado actual, restricciones y trabajo previo
2. **Proponer**: Resultado del brainstorming (arriba)
3. **Planificar**: Tras aprobacion del usuario, detallar pasos y tests esperados
4. **Implementar (TDD)**: Escribir test que falla → implementar minimo → refactorizar
5. **Verificar**: Ejecutar suite, revisar codigo contra checklist §4, comprobar AGENTS.md
6. **Cerrar**: `$cerrar-modulo` si el modulo esta completo; si no, documentar estado parcial

Claude NUNCA asume que puede ejecutar codigo directamente. Proporciona comandos que el usuario ejecuta e interpreta resultados para iterar.

### Depuracion sistematica (4 fases)

Cuando algo falla:

1. **Reproducir**: Obtener el error exacto con pasos minimos y entrada conocida
2. **Aislar**: Determinar componente responsable (busqueda binaria entre capas)
3. **Hipotesis**: Formular 1-2 causas probables y diseñar experimento minimo que las distinga
4. **Verificar fix**: El test que reproducia el fallo ahora pasa; la suite completa no regresiona

No adivinar. No cambiar multiples cosas a la vez. No asumir la causa sin evidencia.

---

## 3. Eficiencia de contexto

### Lectura bajo demanda

- **Siempre cargar**: `AGENTS.md`, `PROJECT_STATE.md` (son breves y criticos).
- **Cargar solo si la tarea lo requiere**: `PLAN_DESARROLLO.md`, `DOCUMENTACION_TECNICA.md`, `GUIA_OPERACION.md`, archivos de `stacks/`.
- **Nunca cargar completo**: `REGISTRO_CAMBIOS.md` (solo ultimas 5-10 entradas), codigo fuente (solo archivos relevantes).

### Cuando resumir vs citar completo

- **Citar completo**: fragmentos de codigo que se van a modificar, mensajes de error exactos, contratos de API.
- **Resumir**: historial de cambios previos, contenido de archivos que solo se consultan como referencia, salida larga de comandos (extraer lo relevante).

### Regla general

Si una pieza de contexto no va a influir en la decision o el codigo de esta tarea, no la cargues. Solicitar contexto especifico es preferible a cargar todo "por si acaso".

---

## 4. Revision de codigo

Antes de entregar codigo final:

- [ ] **Correccion logica**: edge cases, off-by-one, null handling, concurrencia
- [ ] **Seguridad**: secretos, injection, autoridad, OWASP top 10
- [ ] **Rendimiento**: N+1, buffers sin limite, timeouts ausentes, queries sin indice
- [ ] **Estilo**: cumple AGENTS.md §1 (idioma, tipado, docstrings, naming)
- [ ] **Pruebas**: cubren el caso nuevo y no introducen regresiones conocidas
- [ ] **Sin secretos**: ni en codigo, ni en logs, ni en respuestas, ni en comentarios

---

## 5. Gestion de contexto

- Solicitar solo contexto necesario para la tarea actual (archivos, secciones)
- Reutilizar contexto entre iteraciones de la misma tarea
- Comunicar cuando el contexto resulte insuficiente para tomar una decision
- No pedir "todo el proyecto" — pedir secciones especificas

---

## 6. Seguridad de secretos

**NUNCA incluir secretos en prompts, codigo o documentacion.**

1. Detectar donde se necesitan credenciales
2. Documentar el nombre de la variable requerida
3. Instruir como configurar en `.env`
4. Usar `os.getenv("{{PREFIJO_VARIABLES}}_NOMBRE_SECRETO")`
5. Nunca repetir el valor en prompts, codigo ni salida

---

## 7. Consulta de Skills

Cuando una tarea coincida con una Skill:

1. Comunicar: "Voy a consultar la Skill [nombre]"
2. Leer completamente el `SKILL.md` y sus referencias
3. Seguir el protocolo paso a paso
4. Adaptar al contexto actual del proyecto

---

## 8. Comunicacion

Comunicar primero el resultado, luego la evidencia, luego los riesgos:

```
COMPLETADO: [que se hizo en 1 linea]

Que se hizo:
- [detalle 1]
- [detalle 2]

Evidencia:
- [pruebas, comandos ejecutados]

Riesgo: [si aplica]
Siguiente: [paso logico]
```

Cuando una decision no bloquea, adoptar la opcion mas simple y reversible.

---

## 9. Compatibilidad con otros agentes

Estas reglas son compatibles con Antigravity, Codex y otros agentes que usen `AGENTS.md` como base. Las secciones de arquitectura, idioma y autoridad se aplican via `AGENTS.md` directamente — no se duplican aqui.
