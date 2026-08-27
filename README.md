# agent-framework

Framework agentico reutilizable para crear proyectos con agentes de IA, memoria operativa y reglas de desarrollo desde el primer commit.

Extraido inicialmente del proyecto entrevoces. El creador y los verificadores tienen pruebas locales reproducibles; todavia falta validarlo en proyectos piloto reales.

> **Estado de Skills:** todos los archivos bajo `plantilla/.agents/skills/` estan congelados mientras se auditan su procedencia y sus licencias. La CLI de Python es la unica ruta de inicializacion soportada durante esta etapa. El wizard `$iniciar-proyecto` se conserva como material existente, pero no se considera verificado ni debe modificarse por ahora.

---

## 1. Que es esto

Un conjunto de archivos que se copian a cualquier proyecto nuevo para darle al agente:

- **Reglas de proceso — "superpowers" (Nivel 0, siempre activo)**: brainstorming estructurado, TDD red-green-refactor, depuracion sistematica en 4 fases. Viven en `.agents/rules/claude.md §2`. Se decidio no implementarlos como skill separado: son comportamiento base que aplica en toda sesion sin invocacion. No aparecen en el catalogo de stacks/ ni en opcional/. No confundir con skills opcionales como `delegar-entre-agentes`.
- **Estructura de documentacion**: AGENTS.md, PROJECT_STATE.md, REGISTRO_CAMBIOS.md, PLAN_DESARROLLO.md y otros como convencion.
- **Skills agrupados por stack**: guias existentes para FastAPI, Flutter, Next.js, ESP32/firmware y LLM/RAG, pendientes de auditoria individual.
- **Memoria de errores**: skill `lecciones-aprendidas` para no repetir ciclos de depuracion ya resueltos.
- **Creacion segura**: una CLI copia la plantilla, resuelve su contrato, protege `.env`, registra la version de origen e inicializa Git mediante una operacion atomica.
- **Verificacion de memoria**: un comando comprueba documentos obligatorios, placeholders y datos iniciales pendientes.

Niveles de estructura:

```
plantilla/
├── .agents/
│   ├── rules/                   → Reglas base (superpowers, idioma, excepciones)
│   └── skills/
│       ├── cerrar-modulo/       ┐
│       ├── evaluar-agente/      │ Skills de core incluidas en la copia y congeladas
│       ├── iniciar-proyecto/    │ (no hay carpeta "core/" literal)
│       ├── lecciones-aprendidas/┘
│       ├── stacks/
│       │   ├── backend-fastapi/
│       │   │   └── skills/       → fastapi-setup
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
└── documentacion/               → Plan, documentacion tecnica, operacion y prompts
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

- No genera el producto por si mismo: crea su base de trabajo, memoria y contexto.
- No reemplaza revision humana del codigo generado.
- **Domain-packs son stubs**: solo hay estructura reservada, sin contenido operativo.
- **`delegar-entre-agentes` es aspiracional**: vive en `opcional/`, sin evidencia de uso real en entrevoces, y no se activa por defecto. Util solo cuando el agente pierde decisiones importantes que PROJECT_STATE.md no captura (razonamiento en curso, decision a medias). En la practica, PROJECT_STATE.md suele ser suficiente.
- No selecciona ni elimina Skills por stack todavia: la copia conserva el arbol completo, byte por byte.
- No certifica las Skills existentes: su calidad, procedencia y licencia siguen pendientes de auditoria.
- No cubre Prisma, pandas/ML, Go, Rust ni infraestructura/DevOps con Skills dedicadas.

---

## 3. Como iniciar un proyecto nuevo

`agent-framework/` se conserva como fuente. Cada proyecto se crea en un directorio nuevo, separado y fuera de este repositorio. No se debe copiar por carpetas manualmente en el flujo normal: el creador prepara un temporal, valida la inicializacion y solo publica el destino cuando toda la operacion termina.

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

### Flujo recomendado: configuracion completa

1. Copia el ejemplo fuera del repositorio y edita sus valores.

```powershell
Copy-Item .\ejemplos\configuracion_proyecto.ejemplo.json D:\PROYECTOS\configuracion-mi-proyecto.json
```

2. Desde la raiz de `agent-framework`, ejecuta:

```powershell
python scripts\crear_proyecto.py D:\PROYECTOS\mi-proyecto "Mi Proyecto" --configuracion D:\PROYECTOS\configuracion-mi-proyecto.json
```

El destino no debe existir. El nombre visible puede contener espacios o acentos; el inicializador deriva por separado los identificadores tecnicos. El comando copia la plantilla completa, crea `.env` ignorado por Git, sustituye los valores declarados, registra `.estado-plantilla.json` e inicializa un repositorio Git sin realizar commits.

3. Verifica la memoria generada antes del primer commit:

```powershell
python D:\PROYECTOS\mi-proyecto\scripts\verificar_memoria_proyecto.py D:\PROYECTOS\mi-proyecto
```

4. Revisa `.env`, abre el proyecto y crea el primer commit:

```powershell
Set-Location D:\PROYECTOS\mi-proyecto
git status
git add -A
git commit -m "init: crea la base del proyecto"
```

### Flujo exploratorio con datos pendientes

Se puede generar una instancia provisional con:

```powershell
python scripts\crear_proyecto.py D:\PROYECTOS\mi-proyecto "Mi Proyecto" --permitir-pendientes
```

Los datos obligatorios faltantes se convierten en marcadores `TODO` y quedan registrados en `.estado-plantilla.json`. El verificador devuelve error hasta que se completen; esta modalidad no debe usarse como base de un primer commit comercial.

### Contingencia: copia manual

Si no puede usarse el creador raiz, se puede copiar **todo** el contenido de `plantilla/`, incluidos los archivos ocultos, hacia un directorio nuevo y ejecutar allí:

```powershell
python scripts\inicializar_proyecto.py "Mi Proyecto" "español" --configuracion D:\PROYECTOS\configuracion-mi-proyecto.json
```

No se recomienda copiar carpetas sueltas ni omitir `.agents`, `.gitignore`, `.gitattributes`, `.env.ejemplo`, `.plantilla-framework` o `configuracion_plantilla.json`: todos forman parte del contrato de la instancia.

El respaldo `scripts/inicializar_proyecto.sh` permanece deprecado y no se considera validado en Windows. El wizard `$iniciar-proyecto` permanece congelado y no forma parte del flujo soportado actual.

---

## 4. Uso con cada agente (agnostico por diseño)

El contrato comun consiste en leer `AGENTS.md` y `PROJECT_STATE.md` antes de actuar. El descubrimiento automatico de reglas o Skills depende de cada herramienta y de su version; si no ocurre, los archivos deben adjuntarse como contexto de forma explicita.

### Claude Code

- Se debe confirmar que `AGENTS.md` este presente en el contexto efectivo.
- `.agents/rules/claude.md` contiene el delta previsto para esta herramienta.
- Las Skills se usan solo como documentacion existente y permanecen congeladas durante su auditoria.
- `PROJECT_STATE.md` conserva el estado entre sesiones.

```
# Flujo posterior a la creacion por CLI
> $cerrar-modulo           ← Al terminar un componente
> $lecciones-aprendidas    ← Antes de depurar algo complejo
```

### Antigravity

- `SYSTEM_PROMPT_DELTA_ANTIGRAVITY.md` documenta el delta previsto.
- Se debe comprobar en la version utilizada si descubre `.agents/skills/` y `.agents/rules/` automaticamente.
- Si no los descubre, se deben adjuntar `AGENTS.md` y las reglas relevantes como contexto.

No se asume compatibilidad automatica sin una prueba en la version concreta de la herramienta.

### Codex CLI

- `SYSTEM_PROMPT_DELTA_CODEX.md` documenta el delta previsto.
- Se debe confirmar la lectura efectiva de `AGENTS.md` y `PROJECT_STATE.md`.
- Las Skills se pueden aportar como contexto de referencia cuando finalice su auditoria.

### VS Code con extension de agente (Copilot, Continue, etc.)

- Agrega `AGENTS.md` y `PROJECT_STATE.md` como archivos de contexto en la configuracion de la extension.
- Skills: abre el `SKILL.md` relevante y pasalo como contexto adicional antes de la tarea.
- Las reglas de `.agents/rules/` no se aplican automaticamente — agregarlas al system prompt de la extension o pasarlas manualmente cuando sea relevante.

### Regla general

Si el agente no lee `AGENTS.md` automaticamente, se debe pasar como primer archivo de contexto junto con `PROJECT_STATE.md`.

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

### Core incluido (congelado durante la auditoria)

| Skill | Que hace | Cuando invocar |
|---|---|---|
| `iniciar-proyecto` | Wizard historico congelado y no verificado en el flujo actual | No invocar hasta completar su auditoria |
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
| Git | Inicializar y controlar la instancia generada | Obligatorio |
| Agente compatible con AGENTS.md | Usar el framework | Claude Code, Antigravity, Codex CLI, o cualquier agente que lea el archivo |
| Python 3.9+ | Ejecutar el creador y los verificadores soportados | Funciona desde PowerShell, cmd o la terminal del editor |
| PowerShell / cmd | Ejecutar los comandos en Windows | No realiza la logica de inicializacion |

El flujo soportado requiere Python. Git Bash y perl solo corresponden al respaldo Bash deprecado, que no forma parte de la ruta verificada.

### Validacion local del framework

Desde la raiz del meta-repositorio:

```powershell
python scripts\validar_contrato_plantilla.py
python -m unittest discover -s pruebas -p "prueba_*.py" -v
```

La suite comprueba creacion completa, memoria pendiente, limpieza atomica, rechazo de sobrescritura, proteccion de `.env` e identidad byte por byte de Skills. El workflow `.github/workflows/validacion.yml` ejecuta la misma validacion en Windows y Ubuntu con Python 3.9 y 3.12.

---

## 10. Estado actual y proxima validacion pendiente

Extraido de un unico proyecto real (entrevoces). **Todavia no fue probado en un segundo proyecto.** La creacion atomica, la configuracion completa, el rechazo de pendientes y la inmutabilidad de Skills si fueron comprobados en directorios temporales.

La proxima vez que se use:
1. Documentar las fricciones de la CLI y del proyecto generado en [`PROJECT_STATE.md`](PROJECT_STATE.md), seccion "Que falta".
2. Registrar cualquier defecto de una Skill sin editarla, indicando ruta, fuente probable y efecto observado.
3. Completar la auditoria de procedencia y licencia antes de modificar, agregar, eliminar o redistribuir Skills.

El objetivo es que dos proyectos piloto completen el flujo antes de publicar `v1.0.0`.

---

## Estructura completa de `plantilla/`

```
plantilla/
├── AGENTS.md                                   ← Reglas permanentes (con placeholders)
├── PROJECT_STATE.md                            ← Estado del proyecto (template vacio)
├── .env.ejemplo                                ← Variables de entorno de referencia
├── .plantilla-framework                        ← Centinela para el script de init
├── configuracion_plantilla.json                 ← Contrato canonico de placeholders
├── scripts/
│   ├── inicializar_proyecto.py                 ← Inicializador interno soportado
│   ├── verificar_memoria_proyecto.py           ← Valida memoria y pendientes
│   └── inicializar_proyecto.sh                 ← Respaldo deprecado sin validacion actual
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
│           ├── backend-fastapi/
│           │   ├── LEEME.md
│           │   └── skills/fastapi-setup/SKILL.md
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
        ├── SYSTEM_PROMPT_DELTA_ANTIGRAVITY.md
        ├── SYSTEM_PROMPT_DELTA_CLAUDE.md
        └── SYSTEM_PROMPT_DELTA_CODEX.md
```

Desde la raiz del meta-repositorio tambien existen:

- `scripts/crear_proyecto.py`: creador atomico de una instancia nueva;
- `scripts/validar_contrato_plantilla.py`: validador del contrato de la plantilla;
- `ejemplos/configuracion_proyecto.ejemplo.json`: punto de partida para una configuracion completa;
- `pruebas/prueba_creacion_proyecto.py`: suite integral con biblioteca estandar;
- `.github/workflows/validacion.yml`: matriz de CI para Windows, Ubuntu y dos versiones de Python;
- `ATRIBUCIONES.md`: inventario de procedencia y licencias pendientes.
