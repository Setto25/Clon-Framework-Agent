# agent-framework

Framework agentico reutilizable para arrancar proyectos con agentes de IA (Claude Code, Antigravity, Codex CLI, VS Code con agentes) con disciplina de proceso, documentacion y skills desde el dia uno.

Extraido del proyecto entrevoces. Probado con Claude Code. Pendiente validacion con segundo proyecto real.

---

## 1. Que es esto

Un conjunto de archivos que se copian a cualquier proyecto nuevo para darle al agente:

- **Reglas de proceso — "superpowers" (Nivel 0, siempre activo)**: brainstorming estructurado, TDD red-green-refactor, depuracion sistematica en 4 fases. Viven en `.agents/rules/claude.md §2`. Se decidio no implementarlos como skill separado: son comportamiento base que aplica en toda sesion sin invocacion. No aparecen en el catalogo de stacks/ ni en opcional/. No confundir con skills opcionales como `delegar-entre-agentes`.
- **Estructura de documentacion**: AGENTS.md, PROJECT_STATE.md, REGISTRO_CAMBIOS.md, PLAN_DESARROLLO.md y otros como convencion.
- **Skills vetados por stack**: guias de implementacion con patrones TDD, cobertura actual en Flutter, Next.js, ESP32/firmware y LLM/RAG.
- **Memoria de errores**: skill `lecciones-aprendidas` para no repetir ciclos de depuracion ya resueltos.
- **Wizard de inicializacion**: skill `iniciar-proyecto` que pregunta stack, idioma y prioridades, y activa solo lo relevante.

Niveles de estructura:

```
plantilla/
├── .agents/
│   ├── rules/                   → Reglas siempre activas (superpowers, idioma, excepciones)
│   └── skills/
│       ├── cerrar-modulo/       ┐
│       ├── evaluar-agente/      │ Skills de core — universales, siempre disponibles
│       ├── iniciar-proyecto/    │ (no hay carpeta "core/" literal)
│       ├── lecciones-aprendidas/┘
│       ├── stacks/
│       │   ├── firmware-esp32/
│       │   │   ├── skills/       → desarrollar-firmware, diagnosticar-hardware
│       │   │   └── domain-packs/ → audio-embebido (stub — sin contenido real todavia)
│       │   ├── frontend-nextjs/
│       │   │   └── skills/       → nextjs-fullstack, typescript-react
│       │   ├── ia-llm/
│       │   │   └── skills/       → rag-local, fine-tuning-llm, agentes-multiagent
│       │   └── mobile-flutter/
│       │       └── skills/       → flutter-state-management, performance, animations
│       └── opcional/
│           └── delegar-entre-agentes/ → Aspiracional, sin uso real probado
└── documentacion/               → AGENTS.md, PROJECT_STATE.md, PLAN_DESARROLLO.md, etc.
```

---

## 2. Que SI hace y que NO hace

### SI hace

- Da al agente reglas de proceso para cada sesion (sin necesidad de repetirlas en el prompt).
- Provee skills con patrones concretos de implementacion (TDD, matrices de decision, codigo de ejemplo) para los stacks cubiertos.
- Mantiene continuidad entre sesiones via `PROJECT_STATE.md` (el agente retoma exactamente donde quedo).
- Registra errores con causa raiz no obvia para no repetir el mismo ciclo de depuracion.
- Se adapta al agente disponible: Claude Code, Antigravity, Codex CLI, o cualquier agente que lea AGENTS.md.

### NO hace

- No genera codigo por si mismo — es contexto y guias para el agente.
- No reemplaza revision humana del codigo generado.
- **Domain-packs son stubs**: solo hay estructura reservada, sin contenido operativo.
- **`delegar-entre-agentes` es aspiracional**: vive en `opcional/`, sin evidencia de uso real en entrevoces, y no se activa por defecto. Util solo cuando el agente pierde decisiones importantes que PROJECT_STATE.md no captura (razonamiento en curso, decision a medias). En la practica, PROJECT_STATE.md suele ser suficiente.
- No cubre todos los stacks: faltan backend-fastapi (hay reglas generales pero no skill dedicado), Prisma, pandas/ML, Go, Rust, infraestructura/DevOps.

---

## 3. Flujo recomendado: como iniciar un proyecto nuevo

### Concepto clave

`agent-framework/` se queda intacto como fuente. Para cada proyecto nuevo se crea un directorio separado y se copia el contenido de `plantilla/` ahi. **No se renombra `plantilla/`, no se trabaja dentro de `agent-framework/`.**

```
d:\PROYECTOS\
├── agent-framework\          ← Este repo. Nunca se toca durante el desarrollo de otros proyectos.
│   └── plantilla\            ← Fuente. Nombre fijo. No cambiar.
└── mi-proyecto-nuevo\        ← Proyecto instanciado. Directorio completamente separado.
    ├── AGENTS.md              ← Copiado de plantilla/ e instanciado
    ├── PROJECT_STATE.md       ← Copiado e instanciado
    ├── .agents\               ← Skills y reglas activos para este proyecto
    └── ...
```

### Paso a paso (PowerShell / cmd / terminal de VS Code)

**Paso 1 — Crear el directorio del proyecto nuevo**

En PowerShell:
```powershell
New-Item -ItemType Directory -Path "d:\PROYECTOS\nombre-del-proyecto"
```

En cmd:
```cmd
mkdir d:\PROYECTOS\nombre-del-proyecto
```

**Paso 2 — Copiar el contenido de `plantilla/` al proyecto nuevo**

En PowerShell (conserva archivos ocultos como `.agents/` y `.env.ejemplo`):
```powershell
$origen = "d:\PROYECTOS\agent-framework\plantilla"
$destino = "d:\PROYECTOS\nombre-del-proyecto"

# Copiar todos los archivos y carpetas, incluyendo ocultos
Get-ChildItem -Path $origen -Force | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination $destino -Recurse -Force
}
```

O si prefieres Explorer: copia manualmente el contenido de `plantilla\` (no la carpeta en si, sino todo lo que hay dentro) al directorio del proyecto nuevo. Asegurate de activar "mostrar archivos ocultos" para que `.agents\` se incluya.

> **Importante — usar siempre `Copy-Item` de PowerShell, no `cp -r` de Git Bash.** Se confirmo con prueba A/B que `cp -r` de Git Bash omite archivos de `.agents\rules\` de forma silenciosa en Windows (sin mensaje de error), resultando en una copia incompleta. `Copy-Item -Recurse -Force` copia todos los archivos correctamente.

**Paso 3 — Abrir el proyecto en tu editor**

```powershell
cd d:\PROYECTOS\nombre-del-proyecto
code .    # VS Code
```

**Paso 4 — Inicializar git**

```powershell
git init
git add -A
git commit -m "init: proyecto nombre-del-proyecto desde agent-framework"
```

**Paso 5 — Reemplazar placeholders con el agente**

Abre el proyecto en tu agente de preferencia y escribe:

```
$iniciar-proyecto
```

El skill `iniciar-proyecto` guia al agente para preguntar:
- Nombre real del proyecto
- Idioma de nombres (español, ingles, etc.)
- Stack tecnologico a activar
- Prioridades del MVP

Y rellena todos los `{{placeholders}}` automaticamente.

> **Sin agente disponible:** reemplaza manualmente en estos archivos:
> `AGENTS.md`, `PROJECT_STATE.md`, `documentacion/PLAN_DESARROLLO.md`, `.agents/rules/excepciones_nominales.md`
> Busca `{{` para encontrar todos.

**Paso 6 (alternativa al Paso 5, no adicional) — Script Python para automatizar el reemplazo**

> Si prefieres automatizar el reemplazo sin pasar por el wizard conversacional del agente, usa este script **en lugar del Paso 5, no ademas de el**. Haciendo ambos se duplicara el trabajo y podria generar conflictos en los placeholders.

El script Python funciona directamente desde PowerShell, cmd o la terminal de VS Code — sin necesidad de Git Bash ni perl:

```powershell
cd d:\PROYECTOS\nombre-del-proyecto
python scripts/inicializar_proyecto.py "nombre-del-proyecto" "español"
```

Requiere Python 3.9+ instalado (`python --version` para verificar).

> `.plantilla-framework` ya viene incluido en `plantilla/` y se copia en el Paso 2 junto con el resto (`Get-ChildItem -Force` incluye archivos ocultos). No es necesario crearlo manualmente.

> `scripts/inicializar_proyecto.sh` existe como respaldo (deprecado) para quienes prefieran bash. Requiere Git Bash + perl. Ver comentario de deprecacion al inicio del archivo.

---

## 4. Uso con cada agente (agnóstico por diseño)

El framework funciona igual con cualquier agente porque el contrato es simple: leer `AGENTS.md` antes de actuar. Los mecanismos difieren segun el agente:

### Claude Code

- `AGENTS.md` se carga automaticamente como contexto del proyecto.
- `.agents/rules/claude.md` se carga automaticamente desde `.agents/rules/`.
- Skills: el agente los lee como documentacion cuando la tarea coincide. Se invocan explicitamente escribiendo `$nombre-del-skill` en el chat.
- `PROJECT_STATE.md` se lee al inicio de cada sesion por la regla §1 de `claude.md`.

```
# Flujo tipico en Claude Code
> $iniciar-proyecto        ← Wizard de setup
> $cerrar-modulo           ← Al terminar un componente
> $lecciones-aprendidas    ← Antes de depurar algo complejo
```

### Antigravity

- Descubre skills automaticamente en `.agents/skills/` usando el frontmatter YAML (`name`, `description`).
- Aplica reglas de `.agents/rules/` automaticamente en cada sesion.
- Invocacion: `$nombre-skill` igual que en Claude Code.
- `AGENTS.md` se carga como contexto base.

No requiere configuracion adicional — la estructura de carpetas es el contrato.

### Codex CLI

- Lee `AGENTS.md` al inicio del proyecto.
- Skills se usan como documentacion de referencia (Codex los lee cuando se los pasas como contexto o cuando coincide con la tarea).
- Mismo flujo manual que Claude Code para invocar skills.

### VS Code con extension de agente (Copilot, Continue, etc.)

- Agrega `AGENTS.md` y `PROJECT_STATE.md` como archivos de contexto en la configuracion de la extension.
- Skills: abre el `SKILL.md` relevante y pasalo como contexto adicional antes de la tarea.
- Las reglas de `.agents/rules/` no se aplican automaticamente — agregarlas al system prompt de la extension o pasarlas manualmente cuando sea relevante.

### Regla general

Si el agente lee `AGENTS.md` al inicio, el framework funciona. Si no lo hace automaticamente, pasalo como primer mensaje de contexto.

---

## 5. Como hacer handoff a un chat nuevo (por limite de contexto)

Cuando un chat llega al limite durante el desarrollo, pegar esto al abrir el nuevo:

```
Continuo trabajando en el proyecto [NOMBRE-PROYECTO].
Lee estos archivos en orden antes de actuar:

1. AGENTS.md                              ← reglas permanentes
2. PROJECT_STATE.md                       ← estado actual, siguiente paso
3. documentacion/PLAN_DESARROLLO.md       ← tareas y prioridades

El ultimo cambio completado fue: [DESCRIPCION BREVE].
El siguiente paso pendiente es: [COPIAR TEXTO DE PROJECT_STATE.md §8].

Si necesitas contexto adicional, pide el archivo por ruta exacta.
No leas todo el proyecto.
```

Estos archivos son los del **proyecto instanciado**, no los de `agent-framework/`.

---

## 6. Inventario de skills

### Core (siempre activos en todo proyecto)

| Skill | Que hace | Cuando invocar |
|---|---|---|
| `iniciar-proyecto` | Wizard interactivo: rellena placeholders, selecciona stack, configura proyecto | Al crear un proyecto nuevo desde plantilla |
| `cerrar-modulo` | Documenta modulo terminado: actualiza PROJECT_STATE, plan, registro de cambios | Cuando las pruebas pasan o el usuario aprueba un componente |
| `evaluar-agente` | Evalua un agente: intenciones, tool-use, prompt injection, limites de autoridad | Al crear/modificar prompts o tool-calling |
| `probar-e2e` | Pruebas end-to-end del MVP entre componentes | Al verificar flujos completos (cliente-servidor-dispositivo) |
| `lecciones-aprendidas` | Memoria de errores resueltos con dificultad (causa raiz no obvia) | Antes de depurar error complejo / tras resolver uno con 2+ intentos |

### Por stack

| Stack | Skill | Que hace | Cuando invocar |
|---|---|---|---|
| backend-fastapi | `fastapi-setup` | Setup con uv, estructura router/schema/service, Alembic, pydantic-settings, TDD con pytest | Al iniciar un proyecto FastAPI o al migrar de pip+venv a uv |
| firmware-esp32 | `desarrollar-firmware` | Implementacion segura en ESP32/MicroPython: confirmar hardware, maquina de estados, limites de memoria | Al implementar logica nueva en microcontrolador |
| firmware-esp32 | `diagnosticar-hardware` | Protocolo sistematico desde alimentacion hasta perifericos | Cuando fallo podria ser electrico o de conexion fisica |
| frontend-nextjs | `nextjs-fullstack` | Patrones App Router: Server Components, Server Actions, caching, layouts, error boundaries | Al implementar paginas, mutaciones o API routes en Next.js |
| frontend-nextjs | `typescript-react` | TypeScript estricto en React/Next: props, generics, hooks custom, inferencia | Al definir tipos o resolver errores de tipos |
| ia-llm | `rag-local` | Pipeline RAG local: chunking, embeddings, vector store, retrieval, augmentation | Cuando el LLM necesita responder con documentos propios |
| ia-llm | `fine-tuning-llm` | Fine-tuning con LoRA/QLoRA: preparacion de datos, entrenamiento, evaluacion, export | Al especializar un modelo en dominio o tarea especifica |
| ia-llm | `agentes-multiagent` | Agentes autonomos y multi-agente: ReAct, Plan-and-Execute, tool-use, guardrails | Al implementar agente con herramientas o coordinar multiples agentes |
| mobile-flutter | `flutter-state-management` | BLoC, Riverpod, Provider: criterio de seleccion, patrones con TDD | Al definir arquitectura de estado de una app Flutter |
| mobile-flutter | `flutter-performance` | Optimizacion: rebuilds innecesarios, listas, imagenes, memoria, profiling con DevTools | Cuando hay jank, uso excesivo de memoria, o antes de release |
| mobile-flutter | `flutter-animations` | Animaciones implicitas, explicitas, hero, staggered, physics-based | Al agregar transiciones o feedback visual |

### Opcional (no activar por defecto)

| Skill | Que hace | Cuando considerar |
|---|---|---|
| `delegar-entre-agentes` | Prepara un traspaso documentado entre agentes capturando lo que PROJECT_STATE.md no puede: razonamiento en curso, decisiones a medias | Cuando el contexto del agente se agota en medio de una tarea compleja y PROJECT_STATE.md §8 no alcanza para retomar sin perdida. En la practica rara vez ocurre — PROJECT_STATE.md suele ser suficiente. Sin evidencia de uso real en entrevoces. |

---

## 7. Casos de uso

### Cuando SI tiene sentido

- Proyecto nuevo donde un agente AI es la herramienta principal de desarrollo.
- Proyecto con multiples sesiones de trabajo donde la continuidad de contexto importa.
- Stack cubierto (FastAPI, Flutter, Next.js, ESP32, LLM/RAG) que se beneficia de skills con patrones vetados.
- Quieres disciplina de proceso (TDD, documentacion, cierre de modulos) sin reestablecerla en cada sesion.

### Cuando NO tiene sentido

- Script de una sola vez o automatizacion desechable: la ceremonia de inicializacion no justifica el overhead.
- Prototipo de 1-2 horas que se va a tirar: la documentacion no aporta valor.
- Proyecto con tooling que ya impone su propia estructura (Django con su propia convencion, Rails, etc.).
- Proyecto puramente de datos/notebooks: no hay skill dedicado y las reglas generales no aportan diferencial.

---

## 8. Tecnologias cubiertas

### Con skills dedicados (patrones, TDD, guias concretas)

| Tecnologia | Stack | Skills disponibles |
|---|---|---|
| FastAPI / SQLAlchemy / Alembic / uv | backend-fastapi | fastapi-setup |
| Flutter / Dart | mobile-flutter | state-management, performance, animations |
| Next.js 14+ / TypeScript / React | frontend-nextjs | nextjs-fullstack, typescript-react |
| ESP32 / MicroPython / Arduino IoT | firmware-esp32 | desarrollar-firmware, diagnosticar-hardware |
| LLM / RAG / Fine-tuning / Multi-agente | ia-llm | rag-local, fine-tuning-llm, agentes-multiagent |

### Con reglas generales pero SIN skill dedicado

| Tecnologia | Cobertura |
|---|---|
| Docker / CI/CD | Mencionado en documentacion base (GUIA_OPERACION) pero sin skill propio |

### No cubierto (usar reglas propias del proyecto si se necesita)

Prisma, pandas/scikit-learn, Go, Rust, Java, Kubernetes, Terraform, Storybook, testing de carga.

---

## 9. Requisitos

| Requisito | Para que | Notas |
|---|---|---|
| Git | Control de versiones, safety check del script | Obligatorio |
| Agente compatible con AGENTS.md | Usar el framework | Claude Code, Antigravity, Codex CLI, o cualquier agente que lea el archivo |
| PowerShell / cmd | Copiar la plantilla, inicializar git | Incluido en Windows |
| Python 3.9+ | Correr `inicializar_proyecto.py` (recomendado) | Funciona desde PowerShell/cmd/terminal de VS Code sin configuracion extra |
| Git Bash (opcional) | Correr `inicializar_proyecto.sh` si se prefiere la version bash | Incluido en Git for Windows. El script Python cubre lo mismo sin necesitar bash. |
| perl (opcional) | Solo necesario para `inicializar_proyecto.sh` | Incluido en Git for Windows. No requerido si se usa el script Python. |

El framework funciona sin ningun script — el wizard del agente (`$iniciar-proyecto`) hace lo mismo de forma interactiva.

---

## 10. Estado actual y proxima validacion pendiente

Extraido de un unico proyecto real (entrevoces). **Todavia no fue probado en un segundo proyecto.**

La proxima vez que se use:
1. Documentar fricciones del wizard o del flujo de copia en [`/PROJECT_STATE.md`](PROJECT_STATE.md) §"Que falta".
2. Si un error se repite con causa raiz no obvia, registrar en `.agents/skills/lecciones-aprendidas/referencias/<stack>.md` del proyecto.
3. Si un skill resulta inadecuado, actualizar su `SKILL.md` directamente en `agent-framework/plantilla/`.

El objetivo es que tras 2-3 proyectos reales la plantilla se estabilice.

---

## Estructura completa de `plantilla/`

```
plantilla/
├── AGENTS.md                                   ← Reglas permanentes (con placeholders)
├── PROJECT_STATE.md                            ← Estado del proyecto (template vacio)
├── .env.ejemplo                                ← Variables de entorno de referencia
├── .plantilla-framework                        ← Centinela para el script de init
├── scripts/
│   └── inicializar_proyecto.sh                 ← Script de inicializacion (requiere bash)
├── .agents/
│   ├── rules/
│   │   ├── claude.md                           ← Reglas especificas para Claude
│   │   └── excepciones_nominales.md            ← Terminos tecnicos que van en ingles
│   └── skills/
│       ├── cerrar-modulo/SKILL.md
│       ├── evaluar-agente/SKILL.md
│       ├── iniciar-proyecto/SKILL.md
│       ├── lecciones-aprendidas/
│       │   ├── SKILL.md
│       │   └── referencias/                    ← Un .md por stack (vacios, se llenan con uso)
│       ├── probar-e2e/SKILL.md
│       ├── opcional/
│       │   └── delegar-entre-agentes/SKILL.md
│       └── stacks/
│           ├── firmware-esp32/
│           │   ├── LEEME.md
│           │   ├── skills/desarrollar-firmware/SKILL.md
│           │   ├── skills/diagnosticar-hardware/SKILL.md
│           │   └── domain-packs/audio-embebido/LEEME.md  ← Stub
│           ├── frontend-nextjs/
│           │   ├── LEEME.md
│           │   ├── skills/nextjs-fullstack/SKILL.md
│           │   └── skills/typescript-react/SKILL.md
│           ├── ia-llm/
│           │   ├── LEEME.md
│           │   ├── skills/rag-local/SKILL.md
│           │   ├── skills/fine-tuning-llm/SKILL.md
│           │   └── skills/agentes-multiagent/SKILL.md
│           └── mobile-flutter/
│               ├── LEEME.md
│               ├── skills/flutter-state-management/SKILL.md
│               ├── skills/flutter-performance/SKILL.md
│               └── skills/flutter-animations/SKILL.md
└── documentacion/
    ├── INDICE_LECTURA_AGENTES.md
    ├── PLAN_DESARROLLO.md
    ├── DOCUMENTACION_TECNICA.md
    ├── REGISTRO_CAMBIOS.md
    ├── GUIA_OPERACION.md
    └── prompts/
        ├── SYSTEM_PROMPT_BASE.md
        └── SYSTEM_PROMPT_ENTREVOCES.md         ← Ejemplo de delta por proyecto
```
