# agent-framework

Framework agentico reutilizable para crear proyectos con agentes de IA, memoria operativa y reglas de desarrollo desde el primer commit.

Extraido inicialmente del proyecto entrevoces. El creador y los verificadores tienen pruebas locales reproducibles, dos pilotos privados completados y una matriz de CI aprobada en Windows y Ubuntu con Python 3.9 y 3.12.

> **Estado de Skills:** las 23 Skills permanecen en el catalogo fuente y fueron revisadas estructuralmente. Un proyecto nuevo recibe `cerrar-modulo`, `lecciones-aprendidas`, `optimizar-contexto`, `probar-e2e` y las Skills adicionales confirmadas mediante `--skill`. Su procedencia sigue incompleta, por lo que no se recomienda redistribuirlas.

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

Al cerrar una tarea material, el agente debe ejecutar la puerta distribuida con los comandos y rutas reales. Un código distinto de cero significa que la tarea sigue incompleta:

```powershell
python D:\PROYECTOS\mi-proyecto\scripts\validar_cierre_tarea.py D:\PROYECTOS\mi-proyecto `
  --comando-prueba "<prueba pertinente>" `
  --archivo-modificado "<archivo modificado>" `
  --documento-actualizado "PROJECT_STATE.md" `
  --documento-actualizado "documentacion/PLAN_DESARROLLO.md" `
  --documento-actualizado "documentacion/REGISTRO_CAMBIOS.md" `
  --guia-operacion-revisada
```

Para detalles, flujos alternativos y contingencias, ver §3 mas abajo.

---



## 1. Que es esto

Un conjunto de archivos que se copian a cualquier proyecto nuevo para darle al agente:

- **Reglas de proceso — "superpowers" (Nivel 0, base)**: brainstorming estructurado, TDD red-green-refactor, depuracion sistematica en 4 fases. Viven en `.agents/rules/claude.md §2`. Se decidio no implementarlos como Skill separado: son comportamiento base obligatorio cuando se carga el conjunto de reglas y no requieren invocacion nominal. No aparecen en el catalogo de stacks/ ni en opcional/. No confundir con Skills opcionales como `delegar-entre-agentes`.
- **Estructura de documentacion**: AGENTS.md, PROJECT_STATE.md, REGISTRO_CAMBIOS.md, PLAN_DESARROLLO.md y otros como convencion.
- **Skills agrupados por stack**: guias para FastAPI, Flutter, Next.js, ESP32/firmware y LLM/RAG. Su procedencia se registra en `ATRIBUCIONES.md`; no toda licencia externa esta verificada.
- **Memoria de errores**: skill `lecciones-aprendidas` para no repetir ciclos de depuracion ya resueltos.
- **Higiene de contexto condicional**: skill `optimizar-contexto` para auditorias, depuracion repetitiva y decisiones amplias. No se activa por defecto en implementaciones acotadas; conserva un estado compacto verificable y usa un indice solo si la exploracion ya es necesaria.
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
│           ├── protocolo-debugging/   → Exige diagnostico reproducible antes de corregir
│           └── diagnosticar-tarea/   → Prediagnostico determinista antes del agente
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

El campo historico `ahorro_tokens` siempre conserva la comparacion agregada para permitir leer informes anteriores, pero solo se interpreta como ahorro causal cuando `comparacion_ahorro_valida` es `true`: ambas variantes objetivo deben haber completado todas las repeticiones. Si alguna falla, el informe lo declara en `observaciones` y publica dos diagnosticos separados: `ahorro_tokens_pareados`, calculado solo en repeticiones donde ambas terminaron correctamente, y `ahorro_tokens_por_exito`, que incorpora intentos fallidos para estimar el coste observado por resultado exitoso. Ninguno de esos diagnosticos aprueba por si solo un experimento con eficacia incompleta.

Para capturar una medicion controlada con Gemini API, se deben preparar `experimentos/archivos_control.txt` y `experimentos/archivos_skill.txt` con las rutas relativas que cada variante puede leer. Ambos manifiestos deben contener los archivos obligatorios del repositorio, incluido `AGENTS.md`; solo deben diferir en el contexto adicional cuya necesidad se esta evaluando. La tarea exige una respuesta JSON y una rubrica factual local comprueba rutas obligatorias y condiciones de `LEEME.md`, `ATRIBUCIONES.md`, `plantilla/AGENTS.md` y las excepciones nominales. Esta rubrica mide solo la cobertura documental declarada; no sustituye una revision de implementacion o seguridad. Con `GEMINI_API_KEY` definida solo en la terminal local y `google-genai` instalado, se ejecuta:

```powershell
python scripts\medir_tokens_gemini.py --modelo gemini-3.7-flash
```

El ejecutor realiza tres repeticiones por variante y guarda `resultados/evaluacion_optimizar_contexto_gemini.json`. Muestra el avance, reintenta hasta tres veces los errores temporales del proveedor con espera gradual y registra los reintentos realizados. Registra por separado tokens de entrada, respuesta y razonamiento; suma respuesta y razonamiento en `tokens_salida`, porque ambos forman parte del consumo total. La rubrica deja `pruebas_aprobadas` en `true` solo cuando la respuesta satisface todos sus hechos verificables y conserva sus fallos en `rubrica_fallos`. Esta captura es un proxy de seleccion de contexto estatico: no ejecuta herramientas ni demuestra por si sola que la Skill cambie el comportamiento de un agente. No se deben enviar secretos ni datos sensibles a proveedores configurados en niveles gratuitos.

`scripts/evaluar_agente_gemini.py` realiza una evaluacion causal de tres variantes: `control_puro` descubre el repositorio sin indice ni Skill; `indice` recibe el preanalisis Python sin el protocolo; y `skill` recibe el mismo indice mas el contenido de `optimizar-contexto`. Las tres se juzgan con la misma rubrica y disponen del mismo maximo de doce ejecuciones de herramientas, pero el control puro no recibe anticipadamente las rutas que Python descubrio. Antes de llamar a Gemini, `scripts/analizar_impacto.py` recorre localmente el repositorio, excluye caches, dependencias y resultados, agrupa coincidencias por archivo y conserva un fragmento corto por ruta. Ese recorrido consume CPU local, no tokens de API; el indice serializado si cuenta como entrada en las dos variantes que lo reciben. El control puro no premarca rutas como observadas y debe obtener evidencia mediante herramientas. Una cache evita devolver otra vez resultados de consultas identicas y la traza conserva las operaciones. La rubrica local de `scripts/validar_resultado_agente.py` exige JSON completo, rutas esenciales, evidencia literal, rutas observadas y comandos soportados. La version 5 del adaptador impide reanudar resultados incompatibles y separa la evidencia previa de las correcciones dirigidas.

El indice puede inspeccionarse sin consumir cuota de Gemini:

```powershell
python scripts\analizar_impacto.py optimizar-contexto CORE_AUTOMATICO "core automatico" "Skills opcionales"
```

```powershell
python scripts\evaluar_agente_gemini.py --modelo gemini-3.1-flash-lite
# Solo si una ejecucion v8 previa dejo avance en resultados\evaluacion_sistema_gemini_v8.json:
python scripts\evaluar_agente_gemini.py --modelo gemini-3.1-flash-lite --reanudar
# Para medir variabilidad de forma explicita:
python scripts\evaluar_agente_gemini.py --modelo gemini-3.1-flash-lite --repeticiones 3
```

El escenario audita, sin alterar archivos, la migracion de `optimizar-contexto` desde el core hacia las Skills opcionales. Exige evidencia de rutas, cambios y pruebas para comprobar el coste de descubrimiento, el ahorro del indice y el aporte marginal del protocolo. Registra en cada ejecucion si incluyo el indice, sus dimensiones, las rutas observadas y los caracteres entregados al modelo. Cada repeticion ejecuta las tres variantes; las repeticiones adicionales se solicitan explicitamente para medir variabilidad.

La misma prueba puede ejecutarse directamente con la API de Anthropic. `scripts/evaluar_agente_anthropic.py` conserva las tres variantes, la rubrica y el limite comun de doce herramientas. El indice adjunta rutas requeridas y evidencia literal reutilizable; por eso `indice` y `skill` no reciben herramientas en el primer turno y solo pueden leer patrones rechazados durante una correccion. Al agotar el presupuesto solicita de forma explicita el JSON final sin herramientas; si el modelo aun asi no lo emite antes del limite de turnos, guarda una ejecucion invalida en vez de abortar las variantes restantes. Admite hasta 6.000 tokens de salida, registra la razon de detencion de cada turno y repara una sola respuesta truncada antes de aplicar la rubrica. Tambien desactiva los reintentos internos del SDK para contabilizar los propios y suma como entrada los tokens normales, creados en cache y leidos desde cache. La comparacion debe hacerse dentro del mismo modelo; los conteos brutos entre proveedores no son equivalentes porque usan tokenizadores distintos.

```powershell
python -m pip install -U anthropic google-genai
$claveAnthropic = Read-Host "Pega tu clave de Anthropic"
$env:ANTHROPIC_API_KEY = $claveAnthropic.Trim()
python scripts\evaluar_agente_anthropic.py --modelo claude-sonnet-4-6 --salida resultados\evaluacion_agente_anthropic_sonnet_v6_corregida.json
python scripts\evaluar_eficacia_skills.py resultados\evaluacion_agente_anthropic_sonnet_v6_corregida.json --salida resultados\informe_agente_anthropic_sonnet_v6_corregida.json
```

Los archivos v6 y v7 son historicos de dos variantes. El experimento causal nuevo debe usar otra salida:

```powershell
python scripts\evaluar_agente_anthropic.py --modelo claude-sonnet-4-6 --repeticiones 3 --salida resultados\evaluacion_sistema_anthropic_sonnet_v8.json
python scripts\evaluar_eficacia_skills.py resultados\evaluacion_sistema_anthropic_sonnet_v8.json --salida resultados\informe_sistema_anthropic_sonnet_v8.json
```

El informe conserva `ahorro_tokens` como ahorro del sistema completo frente al control puro y agrega `comparaciones`: ahorro del indice frente al control puro, aporte marginal de la Skill frente al indice y diferencias de eficacia para cada salto. Los informes historicos `control`/`skill` siguen siendo legibles, pero no miden el ahorro total del sistema incorporado.

### Escenario aislado de desarrollo web

`scripts/evaluar_desarrollo_web_gemini.py` prueba un contexto distinto a la auditoria estatica: una implementacion de varios archivos y ciclos de prueba sobre un tablero de tareas con backend FastAPI e interfaz HTML/JavaScript. Cada ejecucion copia `pruebas/fixtures/desarrollo-web/` a un directorio temporal independiente. El agente puede leer y reemplazar solo fuentes autorizadas; no puede modificar las pruebas ni el framework. La validacion ejecuta casos funcionales del backend y pruebas Node del contrato de interfaz. Al terminar, la copia temporal se elimina y el resultado conserva tokens, herramientas, traza y salidas de prueba.

La version 3 separa cinco tratamientos: `control_puro`, `indice`, `skill_adaptativa`, `skill_extendida` y `extendido_compacto`. La variante adaptativa recibe solo el selector de `SKILL.md`; la extendida recibe tambien la referencia real `referencias/modo_extendido.md`; y la compacta recibe exclusivamente esa referencia. Asi se mide el valor del selector, el coste de forzar el escalamiento y la carga progresiva sin mantener un protocolo paralelo al distribuido. La aprobacion toma `skill_adaptativa` como tratamiento objetivo frente al control puro; las variantes extendidas son controles diagnosticos y no pueden aprobar una Skill adaptativa ineficaz.

La corrida web v2 demostro por que se cambio la logica: las variantes adaptativa, extendida y compacta ejecutaron la misma secuencia de diez herramientas. Forzar el modo extendido no mejoro la eficacia y la Skill completa consumio entre 88,90 % y 94,17 % mas tokens que el indice. La v3 elimina la activacion preventiva por cuatro lecturas: usa directo o indice hasta observar mas de diez rutas, mas de tres componentes, dos ciclos fallidos, una consulta repetida o presion real de contexto.

El fixture inicial falla deliberadamente y una prueba local demuestra que admite una solucion completa. La simulacion no consume API; la medicion Gemini requiere `google-genai`, FastAPI, httpx y Node.js disponibles en la maquina. Se empieza con una sola repeticion:

```powershell
python scripts\evaluar_desarrollo_web_gemini.py --modelo gemini-3.1-flash-lite --repeticiones 1 --salida resultados\evaluacion_desarrollo_web_gemini_v3.json
python scripts\evaluar_eficacia_skills.py resultados\evaluacion_desarrollo_web_gemini_v3.json --salida resultados\informe_desarrollo_web_gemini_v3.json
```

Tambien puede medirse el mismo escenario mediante Qwen Model Studio y su API compatible con OpenAI. El adaptador v4 usa `indice_autoritativo`: se genera justo antes de cada tarea y las cuatro variantes que lo reciben no tienen disponible `listar_archivos`. Asi no se atribuye como ahorro una instruccion que el modelo puede ignorar. Por defecto usa `qwen3.7-plus` con `enable_thinking` desactivado. Los tokens de razonamiento se registran como desglose de `completion_tokens`, sin sumarlos por segunda vez. Los tokens solo se comparan dentro del mismo modelo y proveedor.

```powershell
python -m pip install -U openai
$claveQwen = Read-Host "Pega tu clave de Model Studio"
$env:DASHSCOPE_API_KEY = $claveQwen.Trim()
$env:QWEN_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
python scripts\evaluar_desarrollo_web_qwen.py --modelo qwen3.7-plus --repeticiones 1 --salida resultados\evaluacion_desarrollo_web_qwen_plus_v4.json
python scripts\evaluar_eficacia_skills.py resultados\evaluacion_desarrollo_web_qwen_plus_v4.json --salida resultados\informe_desarrollo_web_qwen_plus_v4.json
```

La URL anterior corresponde al alcance internacional. Si la consola de Model Studio entrega otra URL compatible con OpenAI para la region o espacio de trabajo, se debe asignar esa URL a `QWEN_BASE_URL` antes de ejecutar. Para medir el efecto del razonamiento, se debe crear un informe separado agregando `--con-razonamiento`; no se mezclan ambos modos en la misma comparacion.

Para aislar el coste de la guia textual frente a la seleccion determinista, Qwen dispone de una prueba de tres variantes: control puro, indice autoritativo completo y `selector_python_compacto`. Esta ultima recibe solo el modo y rutas editables que Python obtuvo del indice, no `SKILL.md` ni sus referencias.

La opcion `--herramientas-eficientes` compara herramientas actuales con lecturas limitadas a 80 lineas y cache invalidable. El resultado registra bytes de herramientas, truncamientos y aciertos de cache para verificar que la optimizacion se uso realmente. `--indice-eficiente` mide el paquete de indice autoritativo mas busqueda textual y lectura por lote; no atribuye ese ahorro a la Skill por si sola.

La corrida `evaluacion_indice_eficiente_gemini_v2.json` con `gemini-3.8-flash`
redujo el consumo agregado aparente en 47,23 %, pero ninguna variante alcanzo eficacia
estable: ambas aprobaron solo una de tres ejecuciones y lo hicieron en repeticiones
distintas. El control incluyo una ejecucion atipica de 207.339 tokens, mientras una
ejecucion eficiente fallida termino con 15.730. Por ello el informe permanece
rechazado y no demuestra ahorro causal; solo justifica repetir la prueba tras corregir
la estabilidad. Los tokens de razonamiento se conservan dentro del consumo de cada
ejecucion y no deben mezclarse con corridas que desactiven razonamiento.

La repeticion posterior `evaluacion_indice_eficiente_gemini_v5.json`, con el adaptador
v4 y `gemini-3.8-flash`, completo las cinco repeticiones de ambas variantes. El informe
v5 queda aprobado: el indice con herramientas eficientes uso 606.283 tokens frente a
900.941 del control, un ahorro pareado de 32,71 %, con eficacia completa en los cinco
pares. Esta evidencia valida el paquete de indice, busqueda y lectura eficiente para
este fixture; no demuestra que una Skill textual aislada ahorre tokens en cualquier
tarea o modelo.

```powershell
python scripts\evaluar_desarrollo_web_qwen.py --selector-python --modelo qwen3.7-plus --repeticiones 1 --salida resultados\evaluacion_selector_python_qwen_v1.json
python scripts\evaluar_eficacia_skills.py resultados\evaluacion_selector_python_qwen_v1.json --salida resultados\informe_selector_python_qwen_v1.json

python scripts\evaluar_desarrollo_web_qwen.py --indice-eficiente --modelo qwen3.7-plus --repeticiones 3 --salida resultados\evaluacion_indice_eficiente_qwen_v3.json
python scripts\evaluar_eficacia_skills.py resultados\evaluacion_indice_eficiente_qwen_v3.json --salida resultados\informe_indice_eficiente_qwen_v3.json
```

El mismo experimento puede ejecutarse con Claude API. Conserva el fixture, las cinco variantes y la eliminacion verificable de `listar_archivos` para el indice autoritativo. La primera medicion debe usar una repeticion: esta ejecuta cinco agentes y puede consumir credito.

```powershell
python scripts\evaluar_desarrollo_web_anthropic.py --modelo claude-sonnet-5 --repeticiones 1 --salida resultados\evaluacion_desarrollo_web_anthropic_sonnet_v1.json
python scripts\evaluar_eficacia_skills.py resultados\evaluacion_desarrollo_web_anthropic_sonnet_v1.json --salida resultados\informe_desarrollo_web_anthropic_sonnet_v1.json
```

Este escenario permite que la Skill amortice su coste durante lecturas, ediciones y correcciones. El indice es solo una fotografia inicial: los cambios posteriores deben comprobarse mediante las herramientas y las pruebas. No se amplian las repeticiones hasta que las cinco variantes completen la implementacion al menos una vez.

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

Esta contingencia conserva las 23 Skills y no aplica seleccion. No se recomienda copiar carpetas sueltas ni omitir `AGENTS.md`, `CLAUDE.md`, `.agents`, `.gitignore`, `.gitattributes`, `.env.ejemplo`, `.plantilla-framework` o `configuracion_plantilla.json`: todos forman parte del contrato de la instancia.

El inicializador directo valida todos los reemplazos antes de escribir y ejecuta los cambios como una transaccion local. Si falla despues de crear Git, `.env`, estado o directorios auxiliares, restaura la copia y conserva el centinela para permitir un nuevo intento.

Si la copia manual ya contiene `.git`, se admite un repositorio limpio con commits o todavia sin commits. Se rechazan cambios rastreados, cambios preparados y operaciones de merge, rebase, cherry-pick, revert o bisect activas. Los archivos no rastreados se preservan y no bloquean la inicializacion, porque el inicializador solo modifica las rutas declaradas por el contrato.

`scripts/inicializar_proyecto.sh` es solo un adaptador de compatibilidad: localiza Python y delega todos los argumentos en `inicializar_proyecto.py`. `$iniciar-proyecto` puede recomendar desde el catalogo y ejecutar la misma CLI Python; una recomendacion nunca sustituye la confirmacion explicita.

---

## 4. Uso con cada agente (agnostico por diseño)

El contrato comun consiste en leer `AGENTS.md` y `PROJECT_STATE.md` antes de actuar.
La plantilla mantiene una unica copia de cada Skill en `.agents/skills/` y solo genera
wrappers cuando una herramienta exige otra raiz. Las capacidades y permisos de la
sesion siempre se comprueban de forma observable.

| Agente | Reglas | Skills | Integracion de la plantilla |
|---|---|---|---|
| Codex | `AGENTS.md` | `.agents/skills/` | Nativa |
| Cursor | `AGENTS.md` | `.agents/skills/` | Nativa |
| Antigravity | `.agents/rules/` | `.agents/skills/` | Nativa mediante regla puente |
| Claude Code | `CLAUDE.md` | `.claude/skills/` | Adaptadores generados hacia `.agents/skills/` |

### Claude Code

- `CLAUDE.md` importa `AGENTS.md`, `PROJECT_STATE.md` y `.agents/rules/claude.md`.
- La creacion, actualizacion y adicion de Skills generan wrappers en `.claude/skills/`.
- Cada wrapper remite a la Skill canonica; no duplica sus instrucciones.
- Para reparar wrappers ausentes se ejecuta `python scripts/sincronizar_adaptadores_agentes.py .`.

```
# Flujo posterior a la creacion por CLI
> $cerrar-modulo           ← Al terminar un componente
> $lecciones-aprendidas    ← Antes de depurar algo complejo
> $optimizar-contexto      ← Tras repeticion observable, alcance amplio o ciclos fallidos
```

### Antigravity

- `SYSTEM_PROMPT_DELTA_ANTIGRAVITY.md` documenta el delta previsto.
- Descubre las reglas y Skills de `.agents/`.
- `00-contexto-framework.md` enlaza ese descubrimiento con `AGENTS.md` y `PROJECT_STATE.md`.
- Se deben comprobar igualmente las herramientas y permisos concedidos a la sesion.

### Codex CLI

- `SYSTEM_PROMPT_DELTA_CODEX.md` documenta el delta previsto.
- Se debe confirmar la lectura efectiva de `AGENTS.md` y `PROJECT_STATE.md`.
- Las Skills se descubren desde `.agents/skills/` y se cargan bajo demanda.

### Cursor

- Reconoce `AGENTS.md` y descubre las Skills de `.agents/skills/`.
- `SYSTEM_PROMPT_DELTA_CURSOR.md` documenta el delta de operacion.
- En agentes remotos, las Skills deben estar versionadas dentro del proyecto.

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
| `optimizar-contexto` | Conserva estado compacto y evidencia verificable en tareas amplias sin reducir cobertura | Solo ante auditoria, exploracion repetida, mas de 10 rutas o dos ciclos fallidos; no se activa por defecto en implementaciones acotadas |

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
| `diagnosticar-tarea` | Ejecuta un prediagnostico determinista con Python antes del agente. Parsea fallos de pruebas, identifica archivos responsables y genera contexto inicial compacto. | Antes de invocar al agente en tareas con pruebas fallidas o errores reproducibles. Reduce la exploracion y el razonamiento dedicados a descubrir que falla y donde. |

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

El framework se valido en dos pilotos privados: una API de inventario con FastAPI y PostgreSQL, y un panel web de inventario con Next.js que consume esa API local. El fixture Next.js conserva un `package-lock.json` generado desde un arbol limpio para que `npm ci` resuelva las mismas dependencias transitivas en Linux y Windows. La revision `0.2.0-alpha.15` agrega una puerta distribuible de cierre de tarea; sus pruebas de humo interactivas en Codex, Cursor, Antigravity y Claude Code confirmaron descubrimiento de reglas y Skills, una tarea documental minima y cierre valido. La matriz remota `Validacion #14` aprobo en Ubuntu y Windows con Python 3.9 y 3.12, ademas del fixture Next.js con Node 24. El alcance de humo no mide rendimiento ni calidad del modelo. La proteccion efectiva de `main` permanece condicionada por GitHub: el repositorio privado de la cuenta personal requiere una organizacion Team o Enterprise para aplicar reglas de rama.

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
├── CLAUDE.md                                   ← Puente de contexto nativo para Claude Code
├── PROJECT_STATE.md                            ← Estado del proyecto (template vacio)
├── .env.ejemplo                                ← Variables de entorno de referencia
├── .plantilla-framework                        ← Centinela para el script de init
├── configuracion_plantilla.json                 ← Contrato canonico de placeholders
├── scripts/
│   ├── inicializar_proyecto.py                 ← Inicializador interno soportado
│   ├── validar_cierre_tarea.py                  ← Ejecuta pruebas y evidencia de cierre por tarea
│   ├── verificar_memoria_proyecto.py           ← Valida memoria y pendientes
│   ├── generar_indice_contexto.py              ← Rastreador local determinista para optimizar-contexto
│   ├── diagnosticar_tarea.py                   ← Prediagnostico de fallos para diagnosticar-tarea
│   ├── sincronizar_adaptadores_agentes.py      ← Genera wrappers Claude desde Skills canonicas
│   └── inicializar_proyecto.sh                 ← Adaptador opcional hacia Python
├── .agents/
│   ├── rules/
│   │   ├── 00-contexto-framework.md            ← Puente para reglas nativas de Antigravity
│   │   ├── claude.md                           ← Reglas especificas para Claude
│   │   └── excepciones_nominales.md            ← Terminos tecnicos que van en ingles
│   └── skills/
│       ├── cerrar-modulo/SKILL.md
│       ├── evaluar-agente/SKILL.md
│       ├── iniciar-proyecto/SKILL.md
│       ├── lecciones-aprendidas/
│       │   ├── SKILL.md
│       │   └── referencias/                    ← Un .md por stack (vacios, se llenan con uso)
│       ├── optimizar-contexto/
│       │   ├── SKILL.md                         ← Selector liviano
│       │   └── referencias/                    ← Modos extendido y arquitectonico bajo demanda
│       ├── probar-e2e/SKILL.md
│       ├── seguridad-backend/
│       │   ├── SKILL.md
│       │   └── referencias/
│       ├── opcional/
│       │   ├── delegar-entre-agentes/SKILL.md
│       │   ├── protocolo-debugging/SKILL.md
│       │   └── diagnosticar-tarea/SKILL.md
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
├── .claude/skills/                              ← Wrappers generados solo en cada instancia
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
        ├── SYSTEM_PROMPT_DELTA_CODEX.md
        └── SYSTEM_PROMPT_DELTA_CURSOR.md
```

Desde la raiz del meta-repositorio tambien existen:

- `scripts/crear_proyecto.py`: creador atomico de una instancia nueva;
- `scripts/agregar_skills.py`: instalador transaccional de Skills confirmadas en una instancia inicializada;
- `scripts/actualizar_proyecto.py`: actualizador conservador con huellas, deteccion de conflictos y reversion;
- `scripts/catalogo_skills.py`: catalogo tipado para recomendaciones y seleccion explicita;
- `scripts/evaluar_eficacia_skills.py`: comparador pareado de eficacia, tokens, herramientas, tiempo y reintentos;
- `plantilla/scripts/validar_cierre_tarea.py`: puerta distribuible que ejecuta pruebas declaradas y exige evidencia de cierre antes de finalizar una tarea;
- `scripts/medir_tokens_gemini.py`: ejecutor local de una medicion pareada de contexto mediante Gemini API;
- `scripts/analizar_impacto.py`: indice local compacto de referencias para evitar exploraciones agenticas exhaustivas;
- `scripts/evaluar_agente_anthropic.py`: evaluador agentico equivalente mediante Claude Sonnet y Anthropic API;
- `scripts/evaluar_desarrollo_web_gemini.py`: evaluador de desarrollo web aislado con backend, interfaz y pruebas reales mediante Gemini;
- `scripts/evaluar_desarrollo_web_qwen.py`: adaptador Qwen Model Studio con indice autoritativo verificable para el escenario aislado;
- `scripts/evaluar_desarrollo_web_anthropic.py`: adaptador Claude API equivalente para el escenario aislado;
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
- `pruebas/prueba_evaluacion_desarrollo_web.py`: aislamiento, inmutabilidad de pruebas y solucion alcanzable del fixture web;
- `pruebas/prueba_evaluacion_qwen.py`: contrato Qwen simulado, uso de tokens y razonamiento opcional;
- `pruebas/prueba_evaluacion_desarrollo_web_anthropic.py`: contrato Sonnet simulado e indice autoritativo sin API;
- `pruebas/prueba_validacion_resultado_agente.py`: rechazo determinista de rutas inventadas y comandos no comprobables;
- `pruebas/prueba_inventario_skills.py`: control de vigencia del inventario de Skills;
- `pruebas/prueba_calidad_skills.py`: invariantes estructurales y operativas de las 23 Skills;
- `pruebas/prueba_catalogo_skills.py`: politica del core y coherencia entre el catalogo, el README y los LEEME de stacks;
- `pruebas/prueba_compatibilidad_agentes.py`: referencias existentes y capacidades no presupuestas por agente;
- `pruebas/prueba_compatibilidad_python.py`: gramatica Python 3.9 y coherencia de constantes duplicadas;
- `.github/workflows/validacion.yml`: matriz Python para Windows y Ubuntu, mas test, lint y build de Next.js;
- `auditoria/inventario_skills.json`: rutas, tamaños y huellas del contenido auditado;
- `ATRIBUCIONES.md`: inventario de procedencia y licencias pendientes.
