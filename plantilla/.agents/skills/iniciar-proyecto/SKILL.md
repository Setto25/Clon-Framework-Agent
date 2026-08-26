---
name: iniciar-proyecto
description: Guia interactiva para inicializar un nuevo proyecto desde la plantilla. Pregunta al usuario los datos necesarios, rellena todos los placeholders y deja el proyecto listo para trabajar. Usar al copiar la plantilla a un directorio nuevo o cuando el usuario quiera arrancar un proyecto desde cero.
---

# Iniciar proyecto

## Contexto

La plantilla contiene placeholders `{{CLAVE}}` distribuidos en varios archivos. Este skill guia al usuario con preguntas claras y rellena cada placeholder con sus respuestas, eliminando la necesidad de buscarlos manualmente.

## Fase 1: Preguntas obligatorias (automatizables por script)

Preguntar al usuario y registrar sus respuestas:

| # | Pregunta | Placeholder | Default |
|---|----------|-------------|---------|
| 1 | "¿Cómo se llama el proyecto?" | `{{NOMBRE_PROYECTO}}` | — |
| 2 | "¿En qué idioma se nombran archivos, clases y variables?" | `{{IDIOMA_NOMBRES}}` | español |

Con la respuesta 1, derivar automáticamente:
- `{{PROYECTO}}` = mismo valor que NOMBRE_PROYECTO
- `{{PREFIJO_VARIABLES}}` = NOMBRE_PROYECTO en MAYUSCULAS, guiones reemplazados por guion bajo

## Fase 2: Preguntas de contenido (requieren input del usuario)

Preguntar una por una. Si el usuario no tiene respuesta aun, marcar como `TODO` y continuar:

| # | Pregunta | Placeholder | Ejemplo de respuesta |
|---|----------|-------------|---------------------|
| 3 | "Describe el producto en una linea." | `{{DESCRIPCION_PRODUCTO_UNA_LINEA}}` | "Asistente de voz para adultos mayores" |
| 4 | "Describe el producto en un parrafo completo (qué hace, para quién, qué problema resuelve)." | `{{DESCRIPCION_PRODUCTO_COMPLETA}}` | — |
| 5 | "¿Cuál es el objetivo inmediato? (ej: completar MVP, lanzar beta)" | `{{OBJETIVO_INMEDIATO}}` | "Completar MVP funcional" |
| 6 | "Lista las prioridades del MVP en orden (una por linea)." | `{{LISTA_PRIORIDADES_NUMERADA}}` | "1. Audio funcional\n2. Backend estable\n3. Tests E2E" |
| 7 | "¿Qué queda explícitamente FUERA del MVP?" | `{{EXCLUSIONES_MVP}}` | "Multi-idioma, dashboard admin, notificaciones push" |
| 8 | "Describe la arquitectura obligatoria (capas, restricciones, diagrama si aplica)." | `{{SECCION_ARQUITECTURA}}` | — |
| 9 | "¿Hay reglas de arquitectura adicionales? (ej: 'todo pasa por el servicio, nunca acceder al repo directo')" | `{{REGLAS_ARQUITECTURA}}` | — |
| 10 | "Lista las prioridades cortas para AGENTS.md (misma lista u otra version resumida)." | `{{LISTA_PRIORIDADES}}` | — |
| 11 | "¿Algo que excluir del MVP en AGENTS.md?" | `{{EXCLUSIONES_MVP}}` | (reutiliza respuesta 7 si aplica) |

## Fase 3: Preguntas opcionales

| # | Pregunta | Placeholder | Cuando preguntar |
|---|----------|-------------|-----------------|
| 12 | "¿Zona horaria del equipo?" | `{{ZONA_HORARIA}}` | Siempre |
| 13 | "¿Estado inicial del proyecto?" | `{{ESTADO_BREVE}}` | Siempre, default: "Inicializando" |
| 14 | "¿Fase activa?" | `{{FASE_ACTIVA}}` | Siempre, default: "Fase 0 — Setup" |
| 15 | "¿Hay infraestructura o hardware confirmado?" | `{{HARDWARE_O_INFRA}}` | Solo si aplica |
| 16 | "¿Decisiones técnicas ya tomadas? (una por linea)" | `{{LISTA_DECISIONES_NUMERADA}}` | Solo si el usuario las tiene |
| 17 | "¿Tecnologías ya decididas?" | `{{LISTA_TECNOLOGIAS}}` | Solo si el usuario las tiene |

## Fase 4: Ejecucion

Una vez recopiladas las respuestas:

1. Si el script `scripts/inicializar_proyecto.sh` existe y el centinela `.plantilla-framework` esta presente, ejecutar:
   ```bash
   ./scripts/inicializar_proyecto.sh "<NOMBRE_PROYECTO>" "<IDIOMA_NOMBRES>"
   ```
   Esto cubre los placeholders de Fase 1.

2. Reemplazar manualmente (con edicion de archivos) los placeholders de Fase 2 y 3 en:
   - `AGENTS.md`
   - `PROJECT_STATE.md`
   - `documentacion/prompts/SYSTEM_PROMPT_BASE.md`
   - `.agents/rules/excepciones_nominales.md`

3. Para respuestas marcadas como `TODO`, dejar el placeholder con formato:
   ```
   <!-- TODO: {{PLACEHOLDER}} — completar cuando se defina -->
   ```

4. Crear `.env` desde `.env.ejemplo` si no existe.

5. Verificar que no queden `{{` sin resolver (excepto los marcados como TODO):
   ```bash
   grep -rn "{{" --include="*.md" --include="*.yaml" | grep -v "TODO"
   ```

## Fase 5: Seleccion de skills

### Fuente de datos

Leer `.agents/skills/catalogo_skills.json` (generado por `scripts/inicializar_proyecto.sh`).
Si el catalogo no existe, generarlo ejecutando:
```bash
./scripts/inicializar_proyecto.sh "<NOMBRE_PROYECTO>" "<IDIOMA_NOMBRES>"
```
O escanear manualmente la estructura de `.agents/skills/` siguiendo la misma logica.

El catalogo tiene esta estructura:
```json
{
  "core": [{"nombre": "...", "ruta": "...", "descripcion": "..."}],
  "opcional": [{"nombre": "...", "ruta": "...", "descripcion": "..."}],
  "stacks": [
    {
      "stack": "firmware-esp32",
      "descripcion": "Proyectos con dispositivos embebidos...",
      "skills": [{"nombre": "...", "ruta": "...", "descripcion": "..."}]
    }
  ]
}
```

### Paso 1: Confirmar skills core

Mostrar al usuario las skills core descubiertas y confirmar que se mantienen activas.
No preguntar una por una — solo informar: "Estas skills core quedan activas: [lista]".

### Paso 2: Preguntar por stacks (agrupado)

Para cada stack en `catalogo_skills.json["stacks"]`:

1. Presentar el stack con su descripcion:
   "¿Tu proyecto involucra [descripcion del stack]? (ej: firmware-esp32)"

2. Si el usuario dice SI:
   - Listar las skills del stack: "Este stack incluye: [nombre — descripcion] por cada skill"
   - Preguntar: "¿Activo todas, o solo algunas?"
   - Activar las seleccionadas (mover a `.agents/skills/`)
   - Leer el LEEME.md del stack y presentar las reglas adicionales recomendadas
   - Preguntar: "¿Agrego estas reglas a AGENTS.md ahora?"

3. Si el usuario dice NO:
   - Seguir al siguiente stack (no preguntar si eliminar todavia)

### Paso 3: Preguntar por skills opcionales

Para cada skill en `catalogo_skills.json["opcional"]`:
- Presentar: "[nombre] — [descripcion]. ¿Lo necesitas?"
- Si: mover de `opcional/[nombre]/` a `.agents/skills/[nombre]/`
- No: dejar en `opcional/`

### Paso 4: Limpieza

Preguntar UNA VEZ al final:
"¿Elimino los stacks y skills opcionales que no seleccionaste, o los conservo por si los necesitas despues?"
- Eliminar: borrar carpetas no activadas de `stacks/` y `opcional/`
- Conservar: dejar todo en su lugar

### Ejecucion de movimientos

```bash
# Activar skill opcional
mv .agents/skills/opcional/<nombre>/ .agents/skills/<nombre>/

# Activar skill de un stack
mv .agents/skills/stacks/<stack>/<skill>/ .agents/skills/<skill>/

# Eliminar stack no usado
rm -rf .agents/skills/stacks/<stack>/

# Eliminar directorio opcional si queda vacio
rmdir .agents/skills/opcional/ 2>/dev/null || true

# Eliminar directorio stacks si queda vacio
rmdir .agents/skills/stacks/ 2>/dev/null || true

# Eliminar catalogo (ya cumplio su funcion)
rm -f .agents/skills/catalogo_skills.json
```

Despues de mover skills, verificar el arbol resultante:
```bash
ls .agents/skills/
```

## Fase 6: Confirmacion

Mostrar al usuario un resumen:
- Nombre del proyecto
- Placeholders completados (cantidad)
- Placeholders pendientes como TODO (listarlos)
- Skills activadas (listar con descripcion)
- Skills conservadas sin activar (listar)
- Stacks instalados / eliminados / conservados
- Reglas adicionales agregadas a AGENTS.md (si aplica)
- Archivos modificados
- Siguiente paso recomendado

## Reglas

- No inventar respuestas. Si el usuario dice "no sé aun", marcar como TODO.
- No saltar preguntas de Fase 1 — son obligatorias.
- Agrupar preguntas relacionadas si el usuario prefiere ir rapido (ej: "dame nombre, idioma y descripcion corta de una vez").
- Si el usuario ya proporciono informacion antes de invocar este skill, no re-preguntar lo que ya se sabe.
- Confirmar antes de ejecutar los reemplazos y movimientos de skills.
- No eliminar stacks ni skills sin confirmacion explicita del usuario.
- Si el usuario no esta seguro sobre un stack, conservarlo — es mas facil activar despues que recuperar algo eliminado.
- El catalogo JSON es la fuente de verdad para el descubrimiento. No hardcodear nombres de skills en este documento.
