# (c) Estructura de carpetas de la plantilla madre reutilizable

**Fecha:** 2026-08-26

---

## Árbol completo

```
plantilla-framework-agentico/
│
├── AGENTS.md                                    # Capa 1: reglas permanentes parametrizadas
├── PROJECT_STATE.md                             # Capa 1: estado vivo con secciones estándar
├── .env.ejemplo                                 # Capa 1: plantilla {{PREFIJO}}_VARIABLE=
│
├── .agents/
│   ├── claude.yaml                              # Capa 1: config de Claude parametrizada
│   │
│   ├── rules/
│   │   ├── claude.md                            # Capa 1: ciclo de trabajo + superpowers
│   │   └── excepciones_nominales.md             # Capa 1: tabla vacía con formato y 1 ejemplo
│   │
│   └── skills/
│       │
│       ├── cerrar-modulo/                       # Capa 1: patrón genérico de cierre documental
│       │   ├── SKILL.md
│       │   ├── agents/openai.yaml
│       │   └── scripts/
│       │       └── verificar_memoria_proyecto.py
│       │
│       ├── evaluar-agente/                      # Capa 1: patrón genérico de evaluación LLM
│       │   ├── SKILL.md
│       │   ├── agents/openai.yaml
│       │   └── referencias/
│       │       └── casos_evaluacion.md          # Plantilla con categorías vacías
│       │
│       ├── probar-e2e/                          # Capa 1: patrón genérico de prueba E2E
│       │   ├── SKILL.md
│       │   ├── agents/openai.yaml
│       │   └── referencias/
│       │       └── guion_e2e.md                 # Plantilla con estructura vacía
│       │
│       ├── delegar-entre-agentes/               # OPCIONAL — incluir solo si la continuidad por PROJECT_STATE.md no basta
│       │   ├── SKILL.md
│       │   └── agents/openai.yaml
│       │
│       └── packs/                               # Capa 2: paquetes intercambiables por dominio
│           │
│           ├── hardware-firmware-audio/          # Pack para proyectos IoT + audio embebido
│           │   ├── LEEME.md                     # Qué contiene y cuándo usarlo
│           │   ├── desarrollar-firmware/
│           │   │   ├── SKILL.md
│           │   │   ├── agents/openai.yaml
│           │   │   └── referencias/
│           │   │       └── reglas_firmware.md
│           │   ├── diagnosticar-hardware/
│           │   │   ├── SKILL.md
│           │   │   ├── agents/openai.yaml
│           │   │   └── referencias/
│           │   │       └── secuencia_pruebas.md
│           │   └── validar-audio/
│           │       ├── SKILL.md
│           │       ├── agents/openai.yaml
│           │       ├── referencias/
│           │       │   └── contrato_audio.md
│           │       └── scripts/
│           │           ├── inspeccionar_wav.py
│           │           └── generar_audio_prueba.py
│           │
│           └── web-backend/                     # Pack para proyectos API REST + DB
│               ├── LEEME.md
│               └── desarrollar-backend/
│                   ├── SKILL.md
│                   ├── agents/openai.yaml
│                   └── referencias/
│                       └── reglas_backend.md
│
├── documentacion/
│   ├── INDICE_LECTURA_AGENTES.md               # Capa 1: guía de lectura por tipo de tarea
│   ├── GUIA_SECRETOS.md                        # Capa 1: protocolo genérico de secretos
│   ├── GUIA_SESIONES_ANTIGRAVITY.md            # Capa 1: protocolo genérico de sesiones
│   ├── HERRAMIENTAS_AGENTE.md                  # Capa 1: capacidades/limitaciones por agente
│   ├── REGISTRO_CAMBIOS.md                     # Capa 1: formato estándar vacío
│   ├── PLAN_DESARROLLO.md                      # Capa 1+2: plantilla de hitos con {{}}
│   ├── DOCUMENTACION_TECNICA.md                # Capa 3: se llena por instancia (vacío)
│   ├── GUIA_OPERACION.md                       # Capa 2: plantilla de secciones operativas
│   └── prompts/
│       ├── PROMPT_SISTEMA_BASE.md              # Capa 1+2: prompt unificado parametrizado
│       ├── PROMPT_DELTA_CLAUDE.md              # Capa 1: solo limitaciones/modo Claude
│       ├── PROMPT_DELTA_ANTIGRAVITY.md         # Capa 1: solo nota automatización
│       └── PROMPT_DELTA_CODEX.md               # Capa 1: solo nota ejecución autónoma
│
└── scripts/
    └── inicializar_proyecto.sh                  # Reemplaza {{}} por valores concretos
```

---

## Convenciones de la estructura

| Convención | Regla |
|---|---|
| Nombres de carpetas en skills | Sin sufijo de proyecto (`cerrar-modulo`, NO `cerrar-modulo-entrevoces`) |
| Subcarpeta de referencias | Siempre `referencias/` (español) |
| Subcarpeta de scripts | Siempre `scripts/` (excepción técnica documentada) |
| Metadatos Antigravity | Siempre `agents/openai.yaml` dentro de cada skill |
| Packs de dominio | En `.agents/skills/packs/NOMBRE-PACK/` — se copian al nivel de skills al instanciar |
| Documentación base | Sin prefijo de agente (`GUIA_SECRETOS.md`, NO `GUIA_SECRETOS_CLAUDE.md`) |
| Prompts | En `documentacion/prompts/` — base + un delta por agente |
| Placeholders | Formato `{{NOMBRE_EN_MAYUSCULAS}}` — reemplazados por `scripts/inicializar_proyecto.sh` |

---

## Cómo instanciar un proyecto nuevo

```bash
# 1. Copiar la plantilla
cp -r plantilla-framework-agentico/ mi-nuevo-proyecto/
cd mi-nuevo-proyecto/

# 2. Ejecutar inicializador (argumentos posicionales: nombre, idioma)
./scripts/inicializar_proyecto.sh "miproyecto" "español"

# 3. Elegir domain packs
# Copiar packs relevantes al nivel de skills:
cp -r .agents/skills/packs/web-backend/* .agents/skills/
# O para hardware:
cp -r .agents/skills/packs/hardware-firmware-audio/* .agents/skills/

# 4. Eliminar packs no usados
rm -rf .agents/skills/packs/

# 5. Llenar contenido de instancia
# - AGENTS.md §3 (arquitectura)
# - AGENTS.md §4 (prioridades)
# - PROJECT_STATE.md §1-§8
# - documentacion/PLAN_DESARROLLO.md
# - documentacion/prompts/PROMPT_SISTEMA_BASE.md §Arquitectura
```

---

## Comparación: estructura actual vs propuesta

| Concepto | Estructura actual (EntreVoces) | Estructura propuesta (plantilla) |
|---|---|---|
| Reglas permanentes | `AGENTS.md` (105 líneas mixtas) | `AGENTS.md` parametrizado + `excepciones_nominales.md` |
| Prompts de sistema | 3 archivos con 80% duplicado | 1 base + 3 deltas mínimos |
| Índices de lectura | 2 archivos (72 + 261 líneas) | 1 fusionado |
| Skills genéricas | Mezcladas con skills de dominio | Separadas en raíz vs packs/ |
| Nombres de skills | Con sufijo `-entrevoces` | Sin sufijo de proyecto |
| Carpetas de refs | `references/` (incorrecto) | `referencias/` (correcto) |
| Multi-agente | §7 en AGENTS.md + regla redundante | §7 en AGENTS.md + skill `delegar-entre-agentes` |
| Cierre documental | Skill + regla + prompt (triple) | Solo Skill (fuente única) |
