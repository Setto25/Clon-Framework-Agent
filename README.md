# agent-framework

Framework agentico reutilizable para crear proyectos con agentes de IA, memoria operativa y reglas de desarrollo desde el primer commit.

Extraido inicialmente del proyecto entrevoces. El creador y los verificadores tienen pruebas locales reproducibles, dos pilotos privados completados y una matriz de CI aprobada en Windows y Ubuntu con Python 3.9 y 3.12.

> **Estado de Skills:** las 22 Skills permanecen en el catalogo fuente y fueron revisadas estructuralmente. Un proyecto nuevo recibe `cerrar-modulo`, `lecciones-aprendidas`, `optimizar-contexto`, `probar-e2e` y las Skills adicionales confirmadas mediante `--skill`. Su procedencia sigue incompleta, por lo que no se recomienda redistribuirlas.

---

## Guia rapida

**Requisitos:** Git, Python 3.9+ y un agente compatible (Claude, Antigravity, Codex u otro que lea AGENTS.md).

### Inicio asistido (recomendado)

Abre `agent-framework/` en tu IDE con agente y escribe:

```text
Usa el framework ubicado en D:\PROYECTOS\agent-framework para iniciar un proyecto nuevo. Guiame con las preguntas necesarias.
```

El agente conduce una entrevista, recomienda Skills y crea el proyecto tras tu confirmacion.

### Inicio manual

```powershell
python scripts\catalogo_skills.py                          # ver Skills disponibles
python scripts\crear_proyecto.py D:\PROYECTOS\mi-proyecto "Mi Proyecto" --skill fastapi-setup
python D:\PROYECTOS\mi-proyecto\scripts\verificar_memoria_proyecto.py D:\PROYECTOS\mi-proyecto
```

Para detalles, flujos alternativos y contingencias, ver §3 mas abajo.

---



## 1. Que es esto

Un conjunto de archivos que se copian a cualquier proyecto nuevo para darle al agente:

- **Reglas de proceso — "superpowers" (Nivel 0, base)**: brainstorming estructurado, TDD red-green-refactor, depuracion sistematica en 4 fases. Viven en `.agents/rules/claude.md §2`. Se decidio no implementarlos como Skill separado: son comportamiento base obligatorio cuando se carga el conjunto de reglas y no requieren invocacion nominal. No aparecen en el catalogo de stacks/ ni en opcional/. No confundir con Skills opcionales como `delegar-entre-agentes`.
- **Estructura de documentacion**: AGENTS.md, PROJECT_STATE.md, REGISTRO_CAMBIOS.md, PLAN_DESARROLLO.md y otros como convencion.
- **Skills agrupados por stack**: guias para FastAPI, Flutter, Next.js, ESP32/firmware y LLM/RAG. Su procedencia se registra en `ATRIBUCIONES.md`; no toda licencia externa esta verificada.
- **Memoria de errores**: skill `lecciones-aprendidas` para no repetir ciclos de depuracion ya resueltos.
- **Economia de contexto condicional**: skill `optimizar-contexto` con 4 niveles (Sin analisis, Ligero, Extendido, Arquitectonico) para deduplicar consultas en tareas transversales o prolongadas usando el script auxiliar `generar_indice_contexto.py`; no se activa automaticamente en tareas simples.
- **Creacion segura**: una CLI copia la plantilla, resuelve su contrato, protege `.env`, registra la version de origen e inicializa Git mediante una operacion atomica.
- **Verificacion de memoria**: un comando comprueba documentos obligatorios, placeholders y datos iniciales pendientes.
- **Compatibilidad basada en capacidades**: los deltas de agente verifican herramientas, sandbox y descubrimiento real en vez de prometer comportamientos por marca.
- **Inicializacion trazable**: `.env` escapa el nombre visible y el registro inicial enumera la version del framework y las Skills efectivamente instaladas.

Niveles de estructura:

```
plantilla/
├── .agents/
│   ├── rules/                   → Reglas base (superpowers, idioma, excepciones)
│   └── skills/
│       ├── cerrar-modulo/       ┐
│       ├── evaluar-agente/      │ Skills de core disponibles y validadas estructuralmente
│       ├── iniciar-proyecto/    │ (no hay carpeta "core/" literal)
│       ├── lecciones-aprendidas/│
│       ├── optimizar-contexto/  │
│       ├── seguridad-backend/   ┘
│       ├── stacks/
│       │   ├── backend-fastapi/
│       │   │   └── skills/       → fastapi-setup
│       │   ├── firmware-esp32/
│       │   │   ├── skills/       → desarrollar-firmware, diagnosticar-hardware
│       │   │   └── domain-packs/ → audio-embebido (stub — sin contenido real todavia)
│       │   ├── frontend-nextjs/
│       │   │   └── skills/       → diseno-ui-web, nextjs-fullstack, typescript-react
│       │   ├── ia-llm/
│       │   │   └── skills/       → rag-local, fine-tuning-llm, agentes-multiagent
│       │   └── mobile-flutter/
│       │       └── skills/       → diseno-ui-flutter, flutter-state-management, performance, animations
│       └── opcional/
│           ├── delegar-entre-agentes/ → Formaliza traspasos entre agentes distintos
│           └── protocolo-debugging/   → Exige diagnostico reproducible antes de corregir
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
- **`delegar-entre-agentes` es opcional**: vive en `opcional/` y se instala con `--skill delegar-entre-agentes`. Formaliza el traspaso de trabajo entre agentes distintos (Claude, Antigravity, Codex) con protocolo de entrega, recepcion y template rapido. Cuando basta actualizar `PROJECT_STATE.md §8`, no hace falta esta Skill.
- No instala una recomendacion del agente sin confirmacion explicita del usuario.
- No certifica una licencia de redistribucion para las Skills con procedencia externa incompleta. Su estructura, inventario y copia se verifican automaticamente.
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

### Inicio asistido desde un IDE

La ruta mas simple es abrir `D:\PROYECTOS\agent-framework` en VS Code, Antigravity u otro IDE con agente y escribir:

```text
Usa el framework ubicado en D:\PROYECTOS\agent-framework para iniciar un proyecto nuevo. Guiame con las preguntas necesarias.
```

La Skill `iniciar-proyecto` recopila objetivo, usuarios, MVP, exclusiones, infraestructura, destino y siguiente paso. Luego recomienda Skills, muestra el resumen y espera la confirmacion de los nombres exactos antes de crear archivos. El agente prepara internamente la configuracion y ejecuta la misma CLI segura documentada abajo. Si el IDE no descubre Skills de forma automatica, se adjuntan `AGENTS.md`, `PROJECT_STATE.md` y `plantilla/.agents/skills/iniciar-proyecto/SKILL.md` como contexto.

### Uso desde otro PC mediante GitHub

GitHub transporta el meta-repositorio entre computadores; no se clona dentro del proyecto consumidor. Antes de publicar cambios se comprueba la visibilidad del repositorio remoto. Si el contenido debe seguir siendo privado, el repositorio de GitHub tambien debe ser privado.

En el PC que contiene la version validada, primero se revisa que no haya cambios sin registrar y que commits faltan en el remoto:

```powershell
Set-Location D:\PROYECTOS\agent-framework
git status
git log --oneline origin/main..main
```

Solo cuando la persona decide publicar esa version en el remoto configurado se ejecuta:

```powershell
git push origin main
```

En el otro PC se clona el framework una sola vez, en una carpeta propia:

```powershell
Set-Location D:\PROYECTOS
git clone https://github.com/Setto25/agent-framework.git agent-framework
Set-Location D:\PROYECTOS\agent-framework
```

Los repositorios privados solicitan autenticacion de GitHub mediante el administrador de credenciales o el mecanismo configurado en el equipo. Despues se abre `D:\PROYECTOS\agent-framework` en el IDE y se usa el inicio asistido. El proyecto resultante se crea como carpeta hermana, por ejemplo:

```text
D:\PROYECTOS\
├── agent-framework\
└── mi-proyecto\
```

Para recibir actualizaciones posteriores, se ejecuta solamente en la copia de `agent-framework` y con su arbol limpio:

```powershell
Set-Location D:\PROYECTOS\agent-framework
git status
git pull --ff-only origin main
```

Cada proyecto consumidor conserva su propio repositorio Git. Un `git pull` del framework no actualiza automaticamente los proyectos ya creados; las Skills nuevas se incorporan de forma explicita mediante `scripts/agregar_skills.py`.

### Flujo manual: configuracion completa

1. Consulta el catalogo. El agente puede recomendar Skills segun el objetivo y el stack confirmado, pero la persona debe aprobar sus nombres exactos.

```powershell
python scripts\catalogo_skills.py
```

2. Copia el ejemplo fuera del repositorio y edita sus valores.

```powershell
Copy-Item .\ejemplos\configuracion_proyecto.ejemplo.json D:\PROYECTOS\configuracion-mi-proyecto.json
```

3. Desde la raiz de `agent-framework`, ejecuta. Repite `--skill` por cada Skill adicional confirmada:

```powershell
python scripts\crear_proyecto.py D:\PROYECTOS\mi-proyecto "Mi Proyecto" --configuracion D:\PROYECTOS\configuracion-mi-proyecto.json --skill fastapi-setup --skill seguridad-backend
```

El destino no debe existir. El nombre visible puede contener espacios o acentos; el inicializador deriva por separado los identificadores tecnicos. El comando copia la base, instala el core automatico mas la seleccion explicita, crea `.env` ignorado por Git, registra las Skills en `.estado-plantilla.json` e inicializa un repositorio Git sin realizar commits.

Para incorporar una Skill confirmada en un proyecto ya inicializado, sin reinicializarlo:

```powershell
python scripts\agregar_skills.py D:\PROYECTOS\mi-proyecto --skill seguridad-backend
```

El comando valida el estado, copia la Skill y sus referencias de forma transaccional y registra la actualizacion. Rechaza Skills desconocidas, repetidas o ya instaladas.

Para comprobar y aplicar una version nueva del framework sobre archivos administrados de una instancia:

```powershell
python scripts\actualizar_proyecto.py D:\PROYECTOS\mi-proyecto --solo-verificar
python scripts\actualizar_proyecto.py D:\PROYECTOS\mi-proyecto
```

El actualizador reemplaza solamente Skills, scripts operativos y el contrato cuya huella coincida con la ultima version instalada. Si detecta un cambio local, una eliminacion o un enlace, informa el conflicto y no escribe nada. Los proyectos antiguos sin huellas deben ejecutar primero `--solo-verificar --adoptar-estado-actual`, revisar la base registrada y repetir la actualizacion en una segunda operacion.

Las entradas son estrictas: el JSON, los argumentos posicionales y cada `--valor` no pueden definir la misma clave más de una vez. Los campos con origen `derivado` los calcula exclusivamente el inicializador. También se rechazan claves desconocidas, tipos incompatibles y caracteres de control invisibles; los campos multilínea normales conservan saltos de línea y tabulaciones.

En PowerShell, los valores multilínea deben ir en `--configuracion` como cadenas JSON con `\n` real de JSON o como listas de cadenas. No se debe usar `` `n`` dentro de `--valor`: el inicializador lo rechaza para impedir que esa secuencia quede impresa literalmente en la memoria del proyecto.

La plantilla fuente y una copia manual deben ser árboles locales regulares. El creador rechaza enlaces simbólicos, junctions, reparse points y cruces hacia otro sistema de archivos antes de copiar. El destino tampoco puede existir previamente, incluso si solo es un enlace roto. Esta restricción evita leer contenido externo o publicar fuera de los límites resueltos.

La inspección admite como máximo 20 000 entradas, 100 MiB acumulados y 20 MiB por archivo. Los JSON se leen hasta 1 MiB y cada valor configurable admite 100 000 caracteres. Cachés, bytecode, archivos especiales y archivos regulares con `setuid` o `setgid` se rechazan. El creador sanea permisos del temporal, Git dispone de 30 segundos por operación y la inicialización completa de 120 segundos.

Antes del reemplazo final se comprueba nuevamente que el destino siga libre. Esto evita reemplazos accidentales y creaciones concurrentes observables, pero no constituye aislamiento frente a un proceso hostil capaz de modificar el mismo directorio padre exactamente entre la comprobación y la operación atómica del sistema.

4. Verifica la memoria generada antes del primer commit:

```powershell
python D:\PROYECTOS\mi-proyecto\scripts\verificar_memoria_proyecto.py D:\PROYECTOS\mi-proyecto
```

5. Revisa `.env`, abre el proyecto y crea el primer commit:

```powershell
Set-Location D:\PROYECTOS\mi-proyecto
git status
git add -A
git commit -m "init: crea la base del proyecto"
```

### Validacion de un frontend Next.js anidado

Cuando `create-next-app` se instale en `interfaz/` porque la raiz ya contiene la memoria de la plantilla, se valida desde la raiz del framework con:

```powershell
python scripts\validar_frontend_nextjs.py D:\PROYECTOS\mi-proyecto
```

El comando exige los scripts `test`, `lint` y `build` en `interfaz/package.json`, y los ejecuta con `npm` desde ese directorio. `--solo-verificar` comprueba solamente la estructura, sin instalar ni ejecutar dependencias.

### Evaluacion de eficacia y consumo

`scripts/evaluar_eficacia_skills.py` compara observaciones reales pareadas con y sin una Skill. La entrada registra criterios de aceptacion, pruebas, tokens de entrada y salida, llamadas a herramientas, duracion y reintentos.

```powershell
Copy-Item ejemplos\evaluacion_optimizar_contexto.ejemplo.json D:\PROYECTOS\evaluacion-real.json
python scripts\evaluar_eficacia_skills.py D:\PROYECTOS\evaluacion-real.json --salida D:\PROYECTOS\informe-evaluacion.json
```

Los ceros del ejemplo son marcadores y deben reemplazarse por mediciones del proveedor o agente utilizado. El evaluador devuelve `0` solo cuando control y tratamiento satisfacen todas sus ejecuciones y ademas se alcanza el ahorro; esto impide aprobar por igualdad cuando ambas tasas son cero. Devuelve `2` cuando el experimento valido no supera los umbrales y `1` cuando la entrada es invalida. No ejecuta modelos ni presenta datos simulados como evidencia.

Para capturar una medicion controlada con Gemini API, se deben preparar `experimentos/archivos_control.txt` y `experimentos/archivos_skill.txt` con las rutas relativas que cada variante puede leer. Ambos manifiestos deben contener los archivos obligatorios del repositorio, incluido `AGENTS.md`; solo deben diferir en el contexto adicional cuya necesidad se esta evaluando. La tarea exige una respuesta JSON y una rubrica factual local comprueba rutas obligatorias y condiciones de `LEEME.md`, `ATRIBUCIONES.md`, `plantilla/AGENTS.md` y las excepciones nominales. Esta rubrica mide solo la cobertura documental declarada; no sustituye una revision de implementacion o seguridad. Con `GEMINI_API_KEY` definida solo en la terminal local y `google-genai` instalado, se ejecuta:

```powershell
python scripts\medir_tokens_gemini.py --modelo gemini-3.7-flash
```

El ejecutor realiza tres repeticiones por variante y guarda `resultados/evaluacion_optimizar_contexto_gemini.json`. Muestra el avance, reintenta hasta tres veces los errores temporales del proveedor con espera gradual y registra los reintentos realizados. Registra por separado tokens de entrada, respuesta y razonamiento; suma respuesta y razonamiento en `tokens_salida`, porque ambos forman parte del consumo total. La rubrica deja `pruebas_aprobadas` en `true` solo cuando la respuesta satisface todos sus hechos verificables y conserva sus fallos en `rubrica_fallos`. Esta captura es un proxy de seleccion de contexto estatico: no ejecuta herramientas ni demuestra por si sola que la Skill cambie el comportamiento de un agente. No se deben enviar secretos ni datos sensibles a proveedores configurados en niveles gratuitos.

`scripts/evaluar_agente_gemini.py` realiza la evaluacion causal: ejecuta un control sin el protocolo y un tratamiento que recibe la Skill en la instruccion inicial, y acumula el uso de cada turno del modelo. Antes de llamar a Gemini, `scripts/analizar_impacto.py` recorre localmente el repositorio, excluye caches, dependencias y resultados, agrupa las coincidencias por archivo y adjunta un unico fragmento corto por ruta. Ese recorrido consume CPU local, no tokens de API; solo el indice compacto serializado forma parte de la entrada del modelo. Ambas variantes reciben el mismo indice y conservan herramientas acotadas de listar, buscar y leer para completar impactos indirectos. El listado exige un prefijo y rechaza la raiz. Una cache evita devolver otra vez resultados de consultas identicas; la traza registra nombres, argumentos, solicitudes, ejecuciones reales, aciertos y violaciones del protocolo. La rubrica local de `scripts/validar_resultado_agente.py` exige JSON completo, todas las rutas esenciales del escenario, rutas existentes y observadas, un patron literal comprobable por evidencia y comandos soportados antes de marcar `pruebas_aprobadas`. El escenario v6 publica esas mismas rutas dentro de `rutas_requeridas_en_rutas_afectadas`, por lo que el agente conoce exactamente la cobertura que se comprobara. Si la primera respuesta falla sin haber violado el protocolo, recibe una sola ronda de correccion que distingue rutas afectadas de evidencias y exige patrones copiados literalmente; todos sus nuevos tokens y herramientas se contabilizan. Ante el limite temporal gratuito de Gemini espera el tiempo informado por el proveedor y reintenta; guarda cada ejecucion terminada para que una interrupcion no descarte el avance. `--reanudar` conserva solo ejecuciones del escenario vigente y completa las faltantes.

El indice puede inspeccionarse sin consumir cuota de Gemini:

```powershell
python scripts\analizar_impacto.py optimizar-contexto CORE_AUTOMATICO "core automatico" "Skills opcionales"
```

```powershell
python scripts\evaluar_agente_gemini.py --modelo gemini-3.1-flash-lite
# Solo si una ejecucion previa dejo avance en resultados\evaluacion_agente_gemini.json:
python scripts\evaluar_agente_gemini.py --modelo gemini-3.1-flash-lite --reanudar
# Para medir variabilidad de forma explicita:
python scripts\evaluar_agente_gemini.py --modelo gemini-3.1-flash-lite --repeticiones 3
```

El escenario v6 audita, sin alterar archivos, la migracion de `optimizar-contexto` desde el core hacia las Skills opcionales. Exige evidencia de rutas, cambios y pruebas para comprobar si el protocolo amortiza su coste inicial en una tarea transversal. Registra dentro de cada ejecucion el numero de archivos examinados localmente, las coincidencias, las rutas requeridas y los caracteres entregados al modelo. La ejecucion predeterminada usa un par control/tratamiento; las repeticiones adicionales se solicitan explicitamente para no consumir cuota con salidas deterministas identicas.

La misma prueba puede ejecutarse directamente con la API de Anthropic. `scripts/evaluar_agente_anthropic.py` conserva el indice y la rubrica de v6, y limita a cuatro las lecturas locales adicionales porque las rutas y evidencias del indice ya cuentan como observadas. Admite hasta 6.000 tokens de salida, registra la razon de detencion de cada turno y repara una sola respuesta truncada antes de aplicar la rubrica. Tambien desactiva los reintentos internos del SDK para contabilizar los propios y suma como entrada los tokens normales, creados en cache y leidos desde cache. La comparacion control/Skill debe hacerse dentro del mismo modelo; los conteos brutos entre proveedores no son equivalentes porque usan tokenizadores distintos.

```powershell
python -m pip install -U anthropic google-genai
$claveAnthropic = Read-Host "Pega tu clave de Anthropic"
$env:ANTHROPIC_API_KEY = $claveAnthropic.Trim()
python scripts\evaluar_agente_anthropic.py --modelo claude-sonnet-4-6 --salida resultados\evaluacion_agente_anthropic_sonnet_v6_corregida.json
python scripts\evaluar_eficacia_skills.py resultados\evaluacion_agente_anthropic_sonnet_v6_corregida.json --salida resultados\informe_agente_anthropic_sonnet_v6_corregida.json
```

La clave se conserva solo en el proceso actual de PowerShell y no debe pegarse en chats, archivos o resultados. El identificador predeterminado es `claude-sonnet-4-6`. El resultado registra `tokens_cache_creada`, `tokens_cache_leida`, `razones_detencion`, `truncamientos` y herramientas rechazadas por presupuesto. No se debe reanudar un resultado creado con una version anterior del adaptador.

La rubrica factual se aplica automaticamente, pero no sustituye la revision humana de decisiones arquitectonicas. Una respuesta que cite rutas, comandos o pruebas inexistentes se rechaza aunque tenga menor consumo. Los informes locales bajo `resultados/` son evidencia de una corrida concreta y no se versionan.

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

Esta contingencia conserva las 22 Skills y no aplica seleccion. No se recomienda copiar carpetas sueltas ni omitir `.agents`, `.gitignore`, `.gitattributes`, `.env.ejemplo`, `.plantilla-framework` o `configuracion_plantilla.json`: todos forman parte del contrato de la instancia.

El inicializador directo valida todos los reemplazos antes de escribir y ejecuta los cambios como una transaccion local. Si falla despues de crear Git, `.env`, estado o directorios auxiliares, restaura la copia y conserva el centinela para permitir un nuevo intento.

Si la copia manual ya contiene `.git`, se admite un repositorio limpio con commits o todavia sin commits. Se rechazan cambios rastreados, cambios preparados y operaciones de merge, rebase, cherry-pick, revert o bisect activas. Los archivos no rastreados se preservan y no bloquean la inicializacion, porque el inicializador solo modifica las rutas declaradas por el contrato.

`scripts/inicializar_proyecto.sh` es solo un adaptador de compatibilidad: localiza Python y delega todos los argumentos en `inicializar_proyecto.py`. `$iniciar-proyecto` puede recomendar desde el catalogo y ejecutar la misma CLI Python; una recomendacion nunca sustituye la confirmacion explicita.

---

## 4. Uso con cada agente (agnostico por diseño)

El contrato comun consiste en leer `AGENTS.md` y `PROJECT_STATE.md` antes de actuar. El descubrimiento automatico de reglas o Skills depende de cada herramienta y de su version; si no ocurre, los archivos deben adjuntarse como contexto de forma explicita.

### Claude Code

- Se debe confirmar que `AGENTS.md` este presente en el contexto efectivo.
- `.agents/rules/claude.md` contiene el delta previsto para esta herramienta.
- Las Skills se usan como guias revisadas; las acciones externas o sensibles conservan los limites de autoridad del usuario.
- `PROJECT_STATE.md` conserva el estado entre sesiones.

```
# Flujo posterior a la creacion por CLI
> $cerrar-modulo           ← Al terminar un componente
> $lecciones-aprendidas    ← Antes de depurar algo complejo
> $optimizar-contexto      ← En tareas transversales, verbosas o prolongadas
```

### Antigravity

- `SYSTEM_PROMPT_DELTA_ANTIGRAVITY.md` documenta el delta previsto.
- Se debe comprobar en la version utilizada si descubre `.agents/skills/` y `.agents/rules/` automaticamente.
- Si no los descubre, se deben adjuntar `AGENTS.md` y las reglas relevantes como contexto.

No se asume compatibilidad automatica sin una prueba en la version concreta de la herramienta.

### Codex CLI

- `SYSTEM_PROMPT_DELTA_CODEX.md` documenta el delta previsto.
- Se debe confirmar la lectura efectiva de `AGENTS.md` y `PROJECT_STATE.md`.
- Las Skills se pueden aportar como contexto de referencia cuando la tarea coincida con su descripcion.

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

### Core automatico

| Skill | Que hace | Cuando invocar |
|---|---|---|
| `cerrar-modulo` | Documenta modulo terminado: actualiza PROJECT_STATE, plan, registro de cambios | Cuando las pruebas pasan o el usuario aprueba un componente |
| `probar-e2e` | Pruebas end-to-end del MVP entre componentes | Al verificar flujos completos (cliente-servidor-dispositivo) |
| `lecciones-aprendidas` | Memoria de errores resueltos con dificultad (causa raiz no obvia) | Antes de depurar error complejo / tras resolver uno con 2+ intentos |
| `optimizar-contexto` | Deduplica consultas y mantiene evidencia trazable mediante 4 niveles de operacion (incluye uso del script `generar_indice_contexto.py`) | En tareas de varios modulos, herramientas verbosas o sesiones largas; no usar escaneo en tareas simples |

### Core seleccionable explicitamente

| Skill | Que hace | Cuando recomendar |
|---|---|---|
| `iniciar-proyecto` | Interfaz conversacional de la CLI y del catalogo | Cuando el proyecto deba crear otras instancias del framework |
| `evaluar-agente` | Evalua intenciones, tool-use, prompt injection y limites de autoridad | Al crear o modificar agentes, prompts o tool-calling |
| `seguridad-backend` | Modela riesgos y exige controles y pruebas negativas para backends HTTP y APIs | Antes de exponer un backend, autenticar identidades o procesar datos sensibles |

### Por stack

| Stack | Skill | Que hace | Cuando invocar |
|---|---|---|---|
| backend-fastapi | `fastapi-setup` | Setup con uv, estructura router/schema/service, Alembic, pydantic-settings, TDD con pytest | Al iniciar un proyecto FastAPI o al migrar de pip+venv a uv |
| firmware-esp32 | `desarrollar-firmware` | Implementacion segura en ESP32/MicroPython: confirmar hardware, maquina de estados, limites de memoria | Al implementar logica nueva en microcontrolador |
| firmware-esp32 | `diagnosticar-hardware` | Protocolo sistematico desde alimentacion hasta perifericos | Cuando fallo podria ser electrico o de conexion fisica |
| frontend-nextjs | `nextjs-fullstack` | Patrones App Router: Server Components, Server Actions, caching, layouts, error boundaries | Al implementar paginas, mutaciones o API routes en Next.js |
| frontend-nextjs | `diseno-ui-web` | Sistema visual, tokens semanticos, temas y micro-interacciones | Al definir o revisar una interfaz Next.js/Tailwind CSS |
| frontend-nextjs | `typescript-react` | TypeScript estricto en React/Next: props, generics, hooks custom, inferencia | Al definir tipos o resolver errores de tipos |
| ia-llm | `rag-local` | Pipeline RAG local: chunking, embeddings, vector store, retrieval, augmentation | Cuando el LLM necesita responder con documentos propios |
| ia-llm | `fine-tuning-llm` | Fine-tuning con LoRA/QLoRA: preparacion de datos, entrenamiento, evaluacion, export | Al especializar un modelo en dominio o tarea especifica |
| ia-llm | `agentes-multiagent` | Agentes autonomos y multi-agente: ReAct, Plan-and-Execute, tool-use, guardrails | Al implementar agente con herramientas o coordinar multiples agentes |
| mobile-flutter | `flutter-state-management` | BLoC, Riverpod, Provider: criterio de seleccion, patrones con TDD | Al definir arquitectura de estado de una app Flutter |
| mobile-flutter | `diseno-ui-flutter` | Sistema visual, temas dinamicos, movimiento y respuesta tactil nativa | Al definir o revisar una interfaz Flutter |
| mobile-flutter | `flutter-performance` | Optimizacion: rebuilds innecesarios, listas, imagenes, memoria, profiling con DevTools | Cuando hay jank, uso excesivo de memoria, o antes de release |
| mobile-flutter | `flutter-animations` | Animaciones implicitas, explicitas, hero, staggered, physics-based | Al agregar transiciones o feedback visual |

### Opcional (no activar por defecto)

| Skill | Que hace | Cuando considerar |
|---|---|---|
| `delegar-entre-agentes` | Formaliza traspasos entre agentes distintos (Claude, Antigravity, Codex) con protocolo de entrega, recepcion y template rapido | Cuando se cambia de herramienta entre sesiones y hay decisiones activas o razonamiento en curso que PROJECT_STATE.md §8 no alcanza a capturar. Cuando basta actualizar §8, no hace falta esta Skill. |
| `protocolo-debugging` | Exige evidencia, trazabilidad y una prueba que reproduzca el fallo antes de corregir | Cuando un error requiere diagnostico sistematico y se debe evitar corregir por conjetura. |

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
| FastAPI / SQLAlchemy / Alembic / uv | backend-fastapi | fastapi-setup, seguridad-backend (core complementaria) |
| Flutter / Dart | mobile-flutter | diseno-ui-flutter, state-management, performance, animations |
| Next.js 14+ / TypeScript / React | frontend-nextjs | diseno-ui-web, nextjs-fullstack, typescript-react |
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
| Node.js 24 + npm | Validar el fixture Next.js de CI | Solo es necesario para la validacion frontend completa |
| PowerShell / cmd | Ejecutar los comandos en Windows | No realiza la logica de inicializacion |

El flujo soportado requiere Python. Bash es opcional y su adaptador no duplica la logica de inicializacion ni requiere Perl.

### Validacion local del framework

Desde la raiz del meta-repositorio:

```powershell
python scripts\validar_cierre_cambio.py
```

El cierre unico valida el contrato, las dependencias citadas por Skills, los archivos administrados, las referencias documentales, la actualizacion simultanea de README y estado, el formato Git y toda la suite Python. La suite comprueba creacion completa, seleccion exacta de Skills, actualizacion con deteccion de conflictos, evaluaciones pareadas, memoria propia del proyecto, limpieza atomica, proteccion de `.env`, coherencia de limites, gramatica de Python 3.9, vigencia del inventario y ausencia de instrucciones obsoletas o destructivas. La CI ejecuta la misma puerta y tambien instala un fixture Next.js bloqueado para ejecutar test, lint y build.

---

## 10. Estado actual y siguiente uso recomendado

El framework se valido en dos pilotos privados: una API de inventario con FastAPI y PostgreSQL, y un panel web de inventario con Next.js que consume esa API local. La base publicada aprobo la matriz Python; la revision local `0.2.0-alpha.13` agrega evaluacion de Skills, actualizacion transaccional y cierre automatico pendiente de ejecucion remota.

Para el siguiente proyecto privado:

1. Crear la instancia mediante `scripts/crear_proyecto.py` y seleccionar solo las Skills necesarias.
2. Documentar las fricciones de la CLI, las recomendaciones y la seleccion efectiva en el `PROJECT_STATE.md` de la instancia.
3. Registrar cualquier defecto de una Skill, su correccion comprobada y el efecto observado.

La procedencia de algunas Skills externas permanece incompleta. Esto no bloquea el uso privado; solo debe resolverse antes de una redistribucion.

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
│   ├── generar_indice_contexto.py              ← Rastreador local determinista para optimizar-contexto
│   └── inicializar_proyecto.sh                 ← Adaptador opcional hacia Python
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
│       ├── optimizar-contexto/SKILL.md
│       ├── probar-e2e/SKILL.md
│       ├── seguridad-backend/
│       │   ├── SKILL.md
│       │   └── referencias/
│       ├── opcional/
│       │   ├── delegar-entre-agentes/SKILL.md
│       │   └── protocolo-debugging/SKILL.md
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
│           │   ├── skills/diseno-ui-web/SKILL.md
│           │   ├── skills/nextjs-fullstack/SKILL.md
│           │   └── skills/typescript-react/SKILL.md
│           ├── ia-llm/
│           │   ├── LEEME.md
│           │   ├── skills/rag-local/SKILL.md
│           │   ├── skills/fine-tuning-llm/SKILL.md
│           │   └── skills/agentes-multiagent/SKILL.md
│           └── mobile-flutter/
│               ├── LEEME.md
│               ├── skills/diseno-ui-flutter/SKILL.md
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
- `scripts/agregar_skills.py`: instalador transaccional de Skills confirmadas en una instancia inicializada;
- `scripts/actualizar_proyecto.py`: actualizador conservador con huellas, deteccion de conflictos y reversion;
- `scripts/catalogo_skills.py`: catalogo tipado para recomendaciones y seleccion explicita;
- `scripts/evaluar_eficacia_skills.py`: comparador pareado de eficacia, tokens, herramientas, tiempo y reintentos;
- `scripts/medir_tokens_gemini.py`: ejecutor local de una medicion pareada de contexto mediante Gemini API;
- `scripts/analizar_impacto.py`: indice local compacto de referencias para evitar exploraciones agenticas exhaustivas;
- `scripts/evaluar_agente_anthropic.py`: evaluador agentico equivalente mediante Claude Sonnet y Anthropic API;
- `scripts/validar_resultado_agente.py`: rubrica factual local para rutas, evidencia y comandos de auditorias agenticas;
- `scripts/estado_proyecto.py`: calculo comun de huellas para archivos administrados;
- `scripts/validar_cierre_cambio.py`: puerta unica de contrato, registros, referencias, formato y pruebas;
- `scripts/validar_contrato_plantilla.py`: validador del contrato de la plantilla;
- `scripts/inventariar_skills.py`: inventariador determinista con texto UTF-8/LF canonico para reproducibilidad entre sistemas;
- `ejemplos/configuracion_proyecto.ejemplo.json`: punto de partida para una configuracion completa;
- `ejemplos/evaluacion_optimizar_contexto.ejemplo.json`: contrato de captura para un experimento pareado real;
- `pruebas/prueba_actualizacion_proyecto.py`: reemplazos seguros y bloqueo de cambios locales;
- `pruebas/prueba_creacion_proyecto.py`: suite integral con biblioteca estandar;
- `pruebas/prueba_evaluacion_skills.py`: no inferioridad y ahorro medido sin datos inventados;
- `pruebas/prueba_analisis_impacto.py`: cobertura, limites y exclusion de artefactos del indice local;
- `pruebas/prueba_evaluacion_anthropic.py`: adaptador Sonnet simulado, sin solicitudes externas;
- `pruebas/prueba_validacion_resultado_agente.py`: rechazo determinista de rutas inventadas y comandos no comprobables;
- `pruebas/prueba_inventario_skills.py`: control de vigencia del inventario de Skills;
- `pruebas/prueba_calidad_skills.py`: invariantes estructurales y operativas de las 22 Skills;
- `pruebas/prueba_catalogo_skills.py`: politica del core y coherencia entre el catalogo, el README y los LEEME de stacks;
- `pruebas/prueba_compatibilidad_agentes.py`: referencias existentes y capacidades no presupuestas por agente;
- `pruebas/prueba_compatibilidad_python.py`: gramatica Python 3.9 y coherencia de constantes duplicadas;
- `.github/workflows/validacion.yml`: matriz Python para Windows y Ubuntu, mas test, lint y build de Next.js;
- `auditoria/inventario_skills.json`: rutas, tamaños y huellas del contenido auditado;
- `ATRIBUCIONES.md`: inventario de procedencia y licencias pendientes.
