# Plan de migración — De artesanal a framework estructurado

**Aplica a:** EntreVoces (instancia actual)  
**Origen:** Framework artesanal existente  
**Destino:** Framework alfa de 3 capas (meta-framework / domain-pack / instancia)

---

## Fase 1: Correcciones urgentes (sin cambio estructural) ✅ COMPLETADA

**Objetivo:** Eliminar divergencias y errores que causan confusión inmediata.

| Acción | Estado |
|---|---|
| Sincronizar `entrega_antigravity/AGENTS.md` con raíz (§7, excepciones) | ✅ |
| Sincronizar `entrega_antigravity/PROJECT_STATE.md` (H2→H6) | ✅ |
| Eliminar `rules/entrevoces_mvp.md` redundante de raíz | ✅ |
| Renombrar `references/` → `referencias/` en 6 skills | ✅ |
| Actualizar `INDICE_DOCUMENTACION.md` con docs 11-13 | ✅ |
| Agregar referencia a GUIA_OPERACION en rule de antigravity | ✅ |

**Riesgo:** Ninguno — son correcciones de coherencia, no de funcionalidad.

---

## Fase 2: Separar capas en la instancia actual

**Objetivo:** Marcar claramente qué es genérico, qué es domain-pack, y qué es instancia. Sin mover archivos aún — solo anotar.

### Paso 2.1 — Clasificar contenido de AGENTS.md

Agregar comentarios internos que identifiquen cada sección:

```markdown
<!-- CAPA: meta-framework -->
## §1 Estilo y código
...

<!-- CAPA: domain-pack:hardware-firmware-audio -->
## §4.3 Reglas de firmware MicroPython
...

<!-- CAPA: instancia -->
## §5 Prioridades del producto
...
```

### Paso 2.2 — Clasificar skills

| Skill | Capa | Acción |
|---|---|---|
| cerrar-modulo-entrevoces | meta-framework | Renombrar a `cerrar-modulo` (sin sufijo) |
| evaluar-agente-entrevoces | meta-framework | Renombrar a `evaluar-agente` |
| probar-e2e-entrevoces | meta-framework | Renombrar a `probar-e2e` |
| desarrollar-backend-entrevoces | domain-pack | Mantener sufijo, marcar como pack `web-backend` |
| desarrollar-firmware-entrevoces | domain-pack | Mantener sufijo, marcar como pack `hardware-firmware-audio` |
| diagnosticar-hardware-entrevoces | domain-pack | Mantener sufijo, marcar como pack `hardware-firmware-audio` |
| validar-audio-dispositivo | domain-pack | Mantener sufijo, marcar como pack `hardware-firmware-audio` |

### Paso 2.3 — Clasificar rules

| Rule | Capa | Acción |
|---|---|---|
| claude.md | meta-framework + instancia mezclados | Separar en §genérico y §instancia |
| excepciones_nominales.md | instancia | Mantener, es 100% específica de EntreVoces |
| entrevoces_mvp.md (antigravity) | instancia | Mantener como regla Always On del paquete portable |

**Criterio de éxito:** Cada archivo tiene un comentario de capa. `git grep "CAPA:"` devuelve clasificación para todo.

---

## Fase 3: Extraer meta-framework como plantilla

**Objetivo:** Crear la carpeta `plantilla/` con los archivos genéricos parametrizados.

### Paso 3.1 — Copiar y parametrizar archivos genéricos

Archivos a extraer (ya creados en `propuesta framework alfa/plantilla/`):

- `AGENTS.md` → reemplazar contenido específico con `{{placeholders}}`
- `PROJECT_STATE.md` → estructura vacía con secciones estándar
- `.agents/rules/claude.md` → solo secciones genéricas (ciclo, depuración, revisión)
- `.agents/rules/excepciones_nominales.md` → plantilla con obligatorias de herramientas
- `.agents/skills/cerrar-modulo/SKILL.md` → protocolo genérico de cierre
- `.agents/skills/evaluar-agente/SKILL.md` → evaluación genérica
- `.agents/skills/probar-e2e/SKILL.md` → testing genérico
- `.agents/skills/delegar-entre-agentes/SKILL.md` → handoff entre agentes
- `documentacion/prompts/PROMPT_SISTEMA_BASE.md` → prompt unificado parametrizado
- `documentacion/prompts/PROMPT_DELTA_*.md` → deltas por agente

### Paso 3.2 — Crear script de inicialización

`scripts/inicializar_proyecto.sh` que:
1. Acepta nombre de proyecto e idioma como argumentos
2. Reemplaza todos los `{{placeholders}}` en archivos
3. Crea `.env` desde `.env.ejemplo`
4. Crea directorios faltantes
5. Reporta placeholders no resueltos que requieren configuración manual

### Paso 3.3 — Verificar que la plantilla es autosuficiente

Test: ejecutar `inicializar_proyecto.sh miproyecto español` en directorio vacío → debe producir estructura funcional sin errores.

**Criterio de éxito:** La plantilla puede inicializar un proyecto nuevo sin referencia a EntreVoces.

---

## Fase 4: Crear domain-packs

**Objetivo:** Encapsular conocimiento específico de dominio en packs intercambiables.

### Paso 4.1 — Pack `hardware-firmware-audio`

Crear `packs/hardware-firmware-audio/` conteniendo:

```
packs/hardware-firmware-audio/
├── PACK.md                          # Metadatos: nombre, descripción, dependencias
├── reglas/
│   ├── reglas_firmware.md           # Extraído de desarrollar-firmware skill
│   └── contrato_audio.md           # Extraído de validar-audio skill
├── skills/
│   ├── desarrollar-firmware/
│   │   └── SKILL.md
│   ├── diagnosticar-hardware/
│   │   └── SKILL.md
│   └── validar-audio/
│       └── SKILL.md
└── seccion_agents.md                # Fragmento para inyectar en AGENTS.md §4
```

### Paso 4.2 — Pack `web-backend`

Crear `packs/web-backend/` conteniendo:

```
packs/web-backend/
├── PACK.md
├── reglas/
│   └── reglas_backend.md            # Extraído de desarrollar-backend skill
├── skills/
│   └── desarrollar-backend/
│       └── SKILL.md
└── seccion_agents.md
```

### Paso 4.3 — Mecanismo de instalación

Agregar a `inicializar_proyecto.sh`:

```bash
instalar_pack() {
  local pack_dir="$1"
  # Copiar skills del pack a .agents/skills/
  # Copiar reglas del pack a .agents/rules/
  # Inyectar seccion_agents.md en AGENTS.md (marcado con <!-- PACK: nombre -->)
}
```

**Criterio de éxito:** `instalar_pack hardware-firmware-audio` agrega las skills y reglas correctas. `desinstalar_pack` las remueve limpiamente.

---

## Fase 5: Integrar superpowers en instancia actual

**Objetivo:** Aplicar las mejoras del framework nuevo sin romper el flujo existente de EntreVoces.

### Paso 5.1 — Fusionar claude.md actual con versión nueva

La versión actual (362 líneas, 17 secciones) se reduce a ~120 líneas (9 secciones) al:
- Eliminar duplicados de AGENTS.md (arquitectura, idioma — ya están en §1-§4)
- Consolidar ciclo de trabajo disperso en un solo flujo TDD
- Reemplazar depuración ad-hoc por protocolo de 4 pasos
- Expandir checklist de revisión (agregar seguridad, rendimiento explícitos)
- Eliminar secciones informativas que no son reglas ejecutables

### Paso 5.2 — Adoptar prompt modular

1. Reemplazar `PROMPT_SISTEMA_CLAUDE.md` (monolítico) por `PROMPT_SISTEMA_BASE.md` + `PROMPT_DELTA_CLAUDE.md`
2. Reemplazar `PROMPT_SISTEMA_ANTIGRAVITY.md` (monolítico) por `PROMPT_SISTEMA_BASE.md` + `PROMPT_DELTA_ANTIGRAVITY.md`
3. Actualizar `.agents/claude.yaml` para referenciar ambos archivos
4. Actualizar `entrega_antigravity/` para usar la nueva estructura

### Paso 5.3 — Renombrar skills genéricas

```bash
git mv .agents/skills/cerrar-modulo-entrevoces .agents/skills/cerrar-modulo
git mv .agents/skills/evaluar-agente-entrevoces .agents/skills/evaluar-agente
git mv .agents/skills/probar-e2e-entrevoces .agents/skills/probar-e2e
# Actualizar nombre en cada SKILL.md
```

### Paso 5.4 — Agregar skill de handoff

Copiar `delegar-entre-agentes/` desde plantilla a `.agents/skills/`.

**Criterio de éxito:** Todos los agentes siguen funcionando con el nuevo layout. `evaluar-agente` pasa con score ≥80%.

---

## Fase 6: Validar y documentar

**Objetivo:** Confirmar que la migración no rompió nada y dejar documentación actualizada.

### Paso 6.1 — Test de humo completo

1. Abrir proyecto con Antigravity → verifica que descubre skills y rules correctamente
2. Sesión con Claude → verifica que lee la nueva estructura sin confusión
3. Ejecutar skill `$probar-e2e` → verifica que el guion funciona end-to-end
4. Ejecutar skill `$evaluar-agente` → verifica score ≥80%

### Paso 6.2 — Actualizar documentación

- `PROJECT_STATE.md` → reflejar nueva estructura en §3
- `REGISTRO_CAMBIOS.md` → entrada de migración con todos los archivos afectados
- `INDICE_DOCUMENTACION.md` → agregar archivos nuevos/renombrados
- `entrega_antigravity/` → re-sincronizar con nueva estructura

### Paso 6.3 — Commit final

```bash
git add -A
git commit -m "refactor: migrar a framework agéntico alfa de 3 capas

- Separar meta-framework (genérico) de domain-packs (dominio) e instancia
- Integrar ciclo TDD, depuración sistemática y checklist expandido
- Adoptar prompt modular (base + deltas por agente)
- Renombrar skills genéricas (quitar sufijo -entrevoces)
- Agregar skill delegar-entre-agentes
- Crear plantilla reutilizable con script de inicialización"
```

### Paso 6.4 — Crear tag

```bash
git tag -a v0.1.0-framework-alfa -m "Primera versión del framework agéntico estructurado"
```

**Criterio de éxito:** Todos los tests de humo pasan. La documentación refleja el estado real. El tag marca un punto de retorno seguro.

---

## Resumen de riesgo por fase

| Fase | Riesgo | Reversibilidad |
|---|---|---|
| 1 — Correcciones | Nulo | `git revert` |
| 2 — Clasificar | Nulo (solo comentarios) | Borrar comentarios |
| 3 — Extraer plantilla | Bajo (archivos nuevos) | Borrar carpeta `plantilla/` |
| 4 — Domain packs | Bajo (archivos nuevos) | Borrar carpeta `packs/` |
| 5 — Integrar en instancia | Medio (modifica archivos activos) | `git revert` + restore de backup |
| 6 — Validar | Nulo (solo verificación) | N/A |

---

## Orden recomendado de ejecución

Fases 1-3 pueden ejecutarse en una sesión. Fase 4 en otra. Fase 5 requiere backup previo y disponibilidad para testing. Fase 6 inmediatamente después de Fase 5 en la misma sesión.

**Tiempo estimado total:** 2-3 sesiones de trabajo con un agente de ejecución (Antigravity/Codex).
