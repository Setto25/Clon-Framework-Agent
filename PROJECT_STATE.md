# Estado del proyecto: agent-framework

**Ultima actualizacion:** 2026-09-01 (rev 76)
**Estado general:** framework reproducible con 22 Skills, evaluacion de eficacia pareada con Gemini o Anthropic, actualizacion transaccional y cierres Python y Next.js verificables
**Fase activa:** Fase 7 — estabilizacion final de CI remota

## 1. Objetivo

Framework agentico reutilizable extraido del proyecto "entrevoces". Provee una plantilla completa (core + stacks + domain-packs) que un proyecto nuevo puede consumir mediante la CLI Python de la raiz.

## 2. Estructura del repo

```
agent-framework/
├── PROJECT_STATE.md          ← Estado real de ESTE repo (este archivo)
├── analisis/                 ← Documentos de extraccion (historico, no operativo)
│   ├── a_clasificacion_capas.md
│   ├── b_conflictos_redundancias.md
│   ├── c_estructura_plantilla.md
│   ├── d_plan_migracion.md
│   └── historial_decisiones.md  ← 102 decisiones cronologicas extraidas de §4
└── plantilla/                ← La plantilla consumible por proyectos nuevos
    ├── AGENTS.md             (template con {{placeholders}})
    ├── PROJECT_STATE.md      (template vacio — NO es el estado de este repo)
    ├── .agents/
    │   ├── skills/
    │   │   ├── cerrar-modulo/
    │   │   ├── evaluar-agente/
    │   │   ├── iniciar-proyecto/
    │   │   ├── lecciones-aprendidas/
    │   │   ├── optimizar-contexto/
    │   │   ├── seguridad-backend/
    │   │   ├── opcional/
    │   │   │   ├── delegar-entre-agentes/
    │   │   │   └── protocolo-debugging/
    │   │   └── stacks/
    │   └── rules/
    │       ├── claude.md
    │       └── excepciones_nominales.md
    └── documentacion/
```

## 3. Stacks disponibles (completos)

| Stack | Skills | Origen |
|---|---|---|
| `backend-fastapi` | fastapi-setup; seguridad-backend como core complementaria | Creado para el framework (uv, SQLAlchemy, Alembic, pytest, OWASP) |
| `firmware-esp32` | desarrollar-firmware, diagnosticar-hardware | Extraido de entrevoces |
| `frontend-nextjs` | diseno-ui-web, nextjs-fullstack, typescript-react | Creado para el framework |
| `ia-llm` | rag-local, fine-tuning-llm, agentes-multiagent | Creado para el framework |
| `mobile-flutter` | diseno-ui-flutter, flutter-state-management, flutter-performance, flutter-animations | Base Flutter adaptada de spjoshis/claude-code-plugins (licencia pendiente de verificacion) |

Cada stack tiene LEEME.md con reglas adicionales, terminos tecnicos y procedimiento de instalacion.

## 4. Decisiones vigentes

> Historial completo de las 102 decisiones cronologicas: `analisis/historial_decisiones.md`

### Arquitectura

- **Stacks por tecnologia, no por dominio.** Cada stack agrupa Skills por plataforma (FastAPI, Flutter, Next.js, ESP32, LLM).
- **Domain-packs como stubs.** No son activables desde `iniciar-proyecto`. Se materializan manualmente cuando un proyecto los necesite.
- **Core automatico minimo.** Todo proyecto recibe `cerrar-modulo`, `lecciones-aprendidas`, `optimizar-contexto` y `probar-e2e`. Las demas se instalan con `--skill NOMBRE`.
- **Economia condicional sin perdida de cobertura.** `optimizar-contexto` usa cuatro niveles: sin analisis, ligero, extendido y arquitectonico. Se activa automaticamente solo cuando el alcance lo justifica, mantiene evidencia trazable y exige deduplicar consultas. No permite omitir requisitos, seguridad, documentacion obligatoria ni pruebas necesarias.
- **`delegar-entre-agentes` en opcional.** Formaliza traspasos entre agentes (Claude, Antigravity, Codex). Se instala con `--skill delegar-entre-agentes`.
- **`protocolo-debugging` en opcional.** Exige evidencia reproducible y trazabilidad antes de corregir errores. Se instala con `--skill protocolo-debugging`.
- **Coherencia documental obligatoria.** Todo cambio material debe actualizar `PROJECT_STATE.md`, `README.md`, los `LEEME.md` afectados, el inventario y las pruebas correspondientes en el mismo cambio.
- **Recomendacion sin autorizacion implicita.** El agente puede proponer Skills, pero debe obtener confirmacion de nombres exactos antes de instalarlas.

### CLI y contrato

- **Contrato unico de plantilla.** `configuracion_plantilla.json` declara placeholders y `archivos_gestionados`; el creador, el inicializador y el actualizador consumen esa lista sin constantes paralelas. `validar_contrato_plantilla.py` comprueba su uso. Version de contrato: `3`.
- **Creacion atomica.** `crear_proyecto.py` copia a temporal, inicializa, valida y publica solo al terminar. Rechaza sobrescrituras, enlaces, artefactos generados y arboles no regulares.
- **Instalacion posterior transaccional.** `agregar_skills.py` incorpora Skills confirmadas sin reinicializar. Conserva existentes y actualiza `.estado-plantilla.json` atomicamente.
- **Actualizacion conservadora.** `actualizar_proyecto.py` usa huellas administradas para reemplazar Skills, scripts y contrato sin sobrescribir cambios locales; los conflictos bloquean toda escritura.
- **Evaluacion pareada.** `evaluar_eficacia_skills.py` compara control y Skill mediante eficacia, pruebas, tokens, herramientas, duracion y reintentos. Exige que ambas variantes satisfagan todas sus ejecuciones, por lo que no aprueba una igualdad de eficacia en cero. No ejecuta modelos ni fabrica mediciones.
- **Captura Gemini de contexto estatico.** `medir_tokens_gemini.py` usa dos manifiestos de archivos para ejecutar pares de contexto con Gemini API. Ambos incluyen `AGENTS.md` e inventario como contexto obligatorio, exigen JSON y validan rutas obligatorias y condiciones documentales sin usar otro modelo como juez. Conserva los tokens de razonamiento como parte de la salida facturable y reintenta indisponibilidades temporales con espera gradual. No ejecuta herramientas ni atribuye el resultado causalmente a la Skill.
- **Evaluacion Gemini con preanalisis local.** `analizar_impacto.py` recorre el arbol sin usar un modelo, excluye artefactos, agrupa coincidencias por ruta y entrega un fragmento literal acotado. `evaluar_agente_gemini.py` adjunta el mismo indice compacto a control y Skill, registra sus dimensiones, conserva herramientas de lectura para impactos indirectos, agrega el uso de cada turno y deduplica consultas identicas mediante cache. `validar_resultado_agente.py` exige rutas esenciales, evidencia con patron literal presente, rutas observadas y comandos comprobables, y rechaza violaciones del protocolo. El escenario v6 publica en el indice la misma lista de rutas que la rubrica exigira dentro de `rutas_afectadas`; una correccion aclara la coleccion exacta y exige patrones copiados literalmente. Ante una cuota temporal 429 espera la demora indicada, reintenta hasta cuatro veces y guarda cada ejecucion completa; `--reanudar` reutiliza solo avances compatibles con el escenario vigente.
- **Evaluacion Anthropic equivalente.** `evaluar_agente_anthropic.py` ejecuta el mismo escenario v6 con Claude Sonnet mediante la API directa de Anthropic. Reutiliza indice y rubrica, permite hasta cuatro lecturas locales adicionales, admite 6.000 tokens de salida, registra razones de detencion y repara una sola salida truncada antes de evaluarla. Contabiliza entrada, salida y categorias de cache, aplica reintentos observables y permite reanudar solo ejecuciones compatibles con la version del adaptador. Los tokens se comparan entre control y Skill del mismo modelo, no de forma bruta entre tokenizadores distintos.
- **Cierre verificable para cualquier agente.** `validar_cierre_cambio.py` impide cerrar cambios con dependencias de Skills ausentes, scripts sin administrar, referencias documentales obsoletas, documentos obligatorios omitidos, errores de formato o pruebas fallidas. AGENTS.md y CI exigen la misma puerta.
- **Piso Python 3.9.** Se evitan APIs posteriores; una prueba AST lo vigila. CI aprobada en 3.9 y 3.12.

### Seguridad y protecciones

- **Protecciones Git.** `.gitignore` y `.gitattributes` en raiz y `plantilla/`; `.env` ignorado; finales LF.
- **Convenciones sin proveedor supuesto.** Cada agente comprueba herramientas, sandbox y permisos observables en vez de asumir capacidades por marca.
- **Capacidades verificables por agente.** Los deltas de Antigravity, Claude y Codex no atribuyen acceso ni descubrimiento por suposicion.

### Procedencia y licencia

- **Licencia raiz diferida.** No se aplicara una licencia global hasta separar contenido original de adaptaciones con derechos pendientes.
- **Licencia externa `mobile-flutter` pendiente.** La fuente `spjoshis/claude-code-plugins` no mostro licencia verificable. Uso personal permitido; redistribucion bloqueada.
- **Modificacion autorizada para uso personal.** Se pueden mejorar Skills sin eliminarlas, conservando procedencia, inventario y pruebas. No redistribuir mientras la procedencia siga incompleta.

### Validacion

- **CI aprobada para la base anterior.** La matriz remota aprobo Windows y Ubuntu con Python 3.9 y 3.12. La version local de la plantilla avanza a `0.2.0-alpha.13` y requiere CI remota.
- **Dos pilotos cerrados.** `piloto-inventario-api` (FastAPI + PostgreSQL) y `piloto-inventario-web` (Next.js). Fricciones sintetizadas en `auditoria/sintesis_pilotos.md`.
- **Base publicada.** `origin/main` llega hasta `aa55f03`; la rama local contiene tres commits posteriores con delegacion revisada, Skills de diseno UI y protocolo de debugging.
- **Regresion documental local.** La suite comprueba que la cantidad y los nombres del catalogo aparezcan en README y que cada Skill de stack figure en su `LEEME.md`.
- **Implementacion de contexto eficiente.** Se agrego `optimizar-contexto` como Skill core automatica, se conecto con `plantilla/AGENTS.md` y se ampliaron las pruebas del selector y del creador.
- **Validacion local de la revision 53.** `quick_validate.py` aprobo la nueva Skill, el contrato resulto valido y una copia Git temporal con todos los cambios incluidos aprobo las 52 pruebas. En la copia principal, la prueba de inventario permanece bloqueada deliberadamente hasta que el nuevo contenido forme parte de `HEAD`.
- **Revision 54 validada localmente.** Una instantanea Git con todos los cambios aprobo 57 pruebas. El fixture Next.js 16.3.3 aprobo test, ESLint, TypeScript estricto y build de produccion con Node 24; sus nombres impuestos quedaron documentados en `excepciones_nominales.md`. La ejecucion remota del nuevo trabajo sigue pendiente.
- **Revision 66 de optimizacion.** La Skill v2 agrega activacion condicional, modos ligero y extendido, registro compacto, deduplicacion y puertas contra afirmaciones no observadas. El evaluador incorpora cache y rubrica factual local; diez pruebas focalizadas, el contrato y `quick_validate.py` aprobaron. En la suite de 60 casos solo queda el bloqueo conocido del inventario contra `HEAD`, que se resolvera cuando el nuevo contenido se incluya en Git. Falta ejecutar el nuevo par con Gemini.
- **Revision 67 del evaluador.** El primer par de la Skill v2 ahorro 5,93 % (15.386 frente a 16.356 tokens), pero el tratamiento perdio cobertura y ambas variantes hicieron un listado general; no se aprobo. El escenario v3 bloquea esa exploracion, conserva una traza y comprueba cobertura esencial y patrones literales. Sus doce pruebas focalizadas aprobaron; la suite completa aprobo 63 de 64 y solo conserva el bloqueo conocido del inventario contra `HEAD`.
- **Revision 68 de eficacia.** El par v3 redujo 29,04 % los tokens y una a nueve las herramientas del tratamiento frente al control, pero ambas variantes obtuvieron eficacia cero. Se corrigio el falso positivo del comparador y el informe historico ahora queda rechazado. El escenario v4 agrega una unica autocorreccion contabilizada para recuperar cobertura sin ocultar su coste; quince pruebas focalizadas aprobaron y la suite completa aprobo 66 de 67, con el unico bloqueo conocido del inventario contra `HEAD`.
- **Revision 69 de preanalisis local.** El par v4 volvio a fallar la rubrica: el control uso 10.754 tokens totales y el tratamiento 71.662, 6,66 veces mas, debido a que seis turnos y una correccion reenviaron el historial acumulado. Se incorporo `analizar_impacto.py`: en el arbol final examina 112 archivos localmente, cubre las 12 rutas esenciales y condensa 28 rutas en 7.245 caracteres entregados al modelo. El escenario v5 entrega ese indice una vez a ambas variantes y reserva el modelo para interpretacion e impactos indirectos. Diecisiete pruebas focalizadas aprobaron; la suite completa aprobo 70 de 71 y solo conserva el bloqueo conocido del inventario contra `HEAD`.
- **Revision 70 de contrato observable.** El par v5 confirmo el valor del preanalisis: el tratamiento uso 14.826 tokens totales frente a 30.575 del control, un ahorro de 51,51 %, y una herramienta frente a ocho. Respecto del tratamiento v4, redujo 79,31 % sus tokens. Ambas variantes fallaron porque omitieron en `rutas_afectadas` rutas que Python ya habia observado; el contrato no exponia que la rubrica exigia las doce. El escenario v6 agrega la lista exacta al indice, distingue cobertura de evidencia y mantiene una unica correccion contabilizada. El indice enriquecido mide 7.688 caracteres; dieciocho pruebas focalizadas aprobaron y la suite completa aprobo 71 de 72, con el unico bloqueo conocido del inventario contra `HEAD`.
- **Revision 71 de comparacion Sonnet.** El par Gemini v6 logro eficacia completa en control y tratamiento. La Skill uso 16.984 tokens frente a 17.746 del control, ahorro 4,29 %, y ambas variantes hicieron una herramienta y una correccion; no alcanzo el umbral de 20 %. Se agrego el adaptador Anthropic para comprobar si Sonnet reduce correcciones o cambia el aporte marginal de la Skill. Dos pruebas simuladas validan el adaptador sin consumir API; quince pruebas focalizadas aprobaron y la suite completa aprobo 73 de 74, con el unico bloqueo conocido del inventario contra `HEAD`.
- **Revision 72 de compatibilidad Anthropic.** El SDK `anthropic` 1.2.0 retiro `temperature` de `Messages.create`. El adaptador dejo de enviarlo y una prueba simulada comprueba que la solicitud conserve solo parametros admitidos. La CLI, la compilacion y las dos pruebas del adaptador aprobaron sin consumir API.
- **Revision 73 de calibracion Sonnet.** El primer par Anthropic mostro un ahorro aparente de 39,46 % y redujo las solicitudes de herramientas de 24 a 18, pero ambas variantes quedaron rechazadas porque sus dos intentos terminaron con JSON incompleto cerca de 5.500 caracteres. El adaptador eleva el limite de salida de 2.000 a 6.000 tokens, registra `stop_reason`, evita aplicar la rubrica a un corte, permite una reparacion compacta y ejecuta como maximo cuatro lecturas adicionales. El resultado anterior no demuestra ineficacia de la Skill y no se reutiliza al reanudar. Las 22 pruebas focalizadas aprobaron; la suite completa aprobo 75 de 76 y conserva unicamente el bloqueo conocido del inventario contra `HEAD`.
- **Revision 74 de cierre automatico.** El contrato v3 centraliza los archivos administrados e incorpora `generar_indice_contexto.py`; las pruebas cubren creacion, huella, incorporacion en actualizaciones, conflicto con contenido local y migracion desde contrato v2. El inventario se contrasta con la copia de trabajo para poder validar antes del commit. Se elimina el adaptador OpenAI-compatible descartado y se agrega una puerta unica exigida por AGENTS.md y CI. `validar_cierre_cambio.py` aprobo contrato, referencias, formato y las 82 pruebas locales. La medicion Opus de una repeticion aprobo la rubrica con 27,27 % de ahorro, pero se conserva como evidencia preliminar hasta medir variabilidad y otros tipos de tarea.
- **Revision 75 de portabilidad de la rubrica.** La primera CI de `0.2.0-alpha.13` detecto que `validar_resultado_agente.py` comparaba en Windows una raiz sin canonizar con archivos ya resueltos, por lo que rechazaba evidencia existente y ocultaba la comprobacion del patron literal. La rubrica ahora confina y lee mediante la misma ruta canonica. Una regresion reproduce el caso con segmentos redundantes; el cierre comprende 83 pruebas.
- **Revision 76 del fixture Next.js.** La CI posterior detecto un `package-lock.json` que npm aceptaba en Windows por el arbol local, pero rechazaba en Linux porque faltaban entradas transitivas de `@emnapi`. El lockfile se genero otra vez desde un directorio limpio para Linux. `npm ci` instalo 346 paquetes sin vulnerabilidades y el fixture aprobo test, ESLint, TypeScript y build de produccion con Next.js 16.3.3.

## 5. Que falta

- **Validacion con proyecto real.** Dos pilotos independientes completaron sus flujos locales, sus fricciones fueron sintetizadas y el validador frontend se ejecuto de extremo a extremo. Falta validar en CI remota.
- **Stack backend-fastapi.** El piloto uso `fastapi-setup` y valido setup, configuracion tipada, rutas, esquemas, servicio, migraciones, persistencia PostgreSQL y pruebas. Quedan autenticacion y autorizacion fuera de alcance hasta confirmar actores y exposicion.
- **Procedencia de Skills.** La fuente y licencia deben resolverse antes de cualquier redistribucion. Las correcciones para uso personal quedan permitidas y registradas.
- **Validacion funcional.** La estructura y las invariantes de seguridad estan probadas, pero cada Skill tecnica necesita un escenario piloto que mida si mejora el resultado frente a trabajar sin ella.
- **CI remota.** La matriz aprobo Windows y Ubuntu con Python 3.9 y 3.12 en la rama de estabilizacion.
- **Cambios locales posteriores.** Las tres Skills incorporadas despues de `aa55f03` y la sincronizacion documental deben aprobar la CI remota antes de considerarse publicadas.
- **Medicion agentica negativa inicial.** La captura local usa `GEMINI_API_KEY` solo desde el entorno y guarda resultados ignorados por Git. En el escenario corto de incorporar una Skill externa de stack, `gemini-3.1-flash-lite` uso aproximadamente 20 % mas tokens con `optimizar-contexto` (4.117 frente a 3.431 por repeticion), tres llamadas de lectura frente a una y ninguna variante supero la revision humana. El resultado no aprueba la Skill para ese escenario; una tarea mas larga podra medir si el coste inicial se amortiza.
- **Medicion agentica larga negativa.** En la auditoria de migrar `optimizar-contexto` de core a opcional, tres repeticiones con `gemini-3.1-flash-lite` consumieron 11.163 tokens por tratamiento frente a 8.499 por control: 31,3 % mas, con tres llamadas de herramienta frente a dos. Ninguna respuesta se aprobo: ambas variantes inventaron rutas y comandos inexistentes. La duracion del control quedo contaminada por dos reintentos de cuota en una repeticion, por lo que no se usa como comparacion de rendimiento. La Skill no se considera eficaz ni ahorradora para este escenario.

## 6. Siguiente paso logico

Publicar la correccion de portabilidad y aprobar la CI remota de `0.2.0-alpha.13`. Despues, proteger `main`, realizar al menos tres pares con Opus en el escenario transversal y agregar escenarios simple, de implementacion y arquitectonico antes de confirmar el beneficio general de `optimizar-contexto`; cualquier redistribucion sigue condicionada por la procedencia de `mobile-flutter`.
