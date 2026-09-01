# Estado del proyecto: agent-framework

**Ultima actualizacion:** 2026-08-31 (rev 65)
**Estado general:** framework reproducible con 22 Skills, evaluacion de eficacia, captura pareada opcional con Gemini API, actualizacion transaccional y CI frontend localmente verificadas
**Fase activa:** Fase 7 — cierre de validacion local y preparacion de CI

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
- **Economia sin perdida de cobertura.** `optimizar-contexto` usa lectura progresiva, busquedas dirigidas, salidas acotadas y resumen trazable; no permite omitir requisitos, seguridad, documentacion obligatoria ni pruebas necesarias.
- **`delegar-entre-agentes` en opcional.** Formaliza traspasos entre agentes (Claude, Antigravity, Codex). Se instala con `--skill delegar-entre-agentes`.
- **`protocolo-debugging` en opcional.** Exige evidencia reproducible y trazabilidad antes de corregir errores. Se instala con `--skill protocolo-debugging`.
- **Coherencia documental obligatoria.** Todo cambio material debe actualizar `PROJECT_STATE.md`, `README.md`, los `LEEME.md` afectados, el inventario y las pruebas correspondientes en el mismo cambio.
- **Recomendacion sin autorizacion implicita.** El agente puede proponer Skills, pero debe obtener confirmacion de nombres exactos antes de instalarlas.

### CLI y contrato

- **Contrato unico de placeholders.** `configuracion_plantilla.json` declara los campos; `validar_contrato_plantilla.py` comprueba su uso. Version de contrato: `2`.
- **Creacion atomica.** `crear_proyecto.py` copia a temporal, inicializa, valida y publica solo al terminar. Rechaza sobrescrituras, enlaces, artefactos generados y arboles no regulares.
- **Instalacion posterior transaccional.** `agregar_skills.py` incorpora Skills confirmadas sin reinicializar. Conserva existentes y actualiza `.estado-plantilla.json` atomicamente.
- **Actualizacion conservadora.** `actualizar_proyecto.py` usa huellas administradas para reemplazar Skills, scripts y contrato sin sobrescribir cambios locales; los conflictos bloquean toda escritura.
- **Evaluacion pareada.** `evaluar_eficacia_skills.py` compara control y Skill mediante eficacia, pruebas, tokens, herramientas, duracion y reintentos. No ejecuta modelos ni fabrica mediciones.
- **Captura Gemini de contexto estatico.** `medir_tokens_gemini.py` usa dos manifiestos de archivos para ejecutar pares de contexto con Gemini API. Ambos incluyen `AGENTS.md` e inventario como contexto obligatorio, exigen JSON y validan rutas obligatorias y condiciones documentales sin usar otro modelo como juez. Conserva los tokens de razonamiento como parte de la salida facturable y reintenta indisponibilidades temporales con espera gradual. No ejecuta herramientas ni atribuye el resultado causalmente a la Skill.
- **Evaluacion Gemini con herramientas.** `evaluar_agente_gemini.py` ejecuta variantes control y Skill con las mismas herramientas de lectura confinadas al repositorio, agrega el uso de cada turno y conserva las respuestas para una revision humana antes de aprobar eficacia. Ante una cuota temporal 429 espera la demora indicada, reintenta hasta cuatro veces y guarda cada ejecucion completa; `--reanudar` reutiliza solo avances compatibles. El escenario vigente audita la migracion de `optimizar-contexto` desde core a opcional sin alterar archivos.
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

- **CI aprobada para la base anterior.** La matriz remota aprobo Windows y Ubuntu con Python 3.9 y 3.12. La version local de la plantilla avanza a `0.2.0-alpha.12` y requiere CI remota.
- **Dos pilotos cerrados.** `piloto-inventario-api` (FastAPI + PostgreSQL) y `piloto-inventario-web` (Next.js). Fricciones sintetizadas en `auditoria/sintesis_pilotos.md`.
- **Base publicada.** `origin/main` llega hasta `aa55f03`; la rama local contiene tres commits posteriores con delegacion revisada, Skills de diseno UI y protocolo de debugging.
- **Regresion documental local.** La suite comprueba que la cantidad y los nombres del catalogo aparezcan en README y que cada Skill de stack figure en su `LEEME.md`.
- **Implementacion de contexto eficiente.** Se agrego `optimizar-contexto` como Skill core automatica, se conecto con `plantilla/AGENTS.md` y se ampliaron las pruebas del selector y del creador.
- **Validacion local de la revision 53.** `quick_validate.py` aprobo la nueva Skill, el contrato resulto valido y una copia Git temporal con todos los cambios incluidos aprobo las 52 pruebas. En la copia principal, la prueba de inventario permanece bloqueada deliberadamente hasta que el nuevo contenido forme parte de `HEAD`.
- **Revision 54 validada localmente.** Una instantanea Git con todos los cambios aprobo 57 pruebas. El fixture Next.js 16.3.3 aprobo test, ESLint, TypeScript estricto y build de produccion con Node 24; sus nombres impuestos quedaron documentados en `excepciones_nominales.md`. La ejecucion remota del nuevo trabajo sigue pendiente.

## 5. Que falta

- **Validacion con proyecto real.** Dos pilotos independientes completaron sus flujos locales, sus fricciones fueron sintetizadas y el validador frontend se ejecuto de extremo a extremo. Falta validar en CI remota.
- **Stack backend-fastapi.** El piloto uso `fastapi-setup` y valido setup, configuracion tipada, rutas, esquemas, servicio, migraciones, persistencia PostgreSQL y pruebas. Quedan autenticacion y autorizacion fuera de alcance hasta confirmar actores y exposicion.
- **Procedencia de Skills.** La fuente y licencia deben resolverse antes de cualquier redistribucion. Las correcciones para uso personal quedan permitidas y registradas.
- **Validacion funcional.** La estructura y las invariantes de seguridad estan probadas, pero cada Skill tecnica necesita un escenario piloto que mida si mejora el resultado frente a trabajar sin ella.
- **CI remota.** La matriz aprobo Windows y Ubuntu con Python 3.9 y 3.12 en la rama de estabilizacion.
- **Cambios locales posteriores.** Las tres Skills incorporadas despues de `aa55f03` y la sincronizacion documental deben aprobar la CI remota antes de considerarse publicadas.
- **Medicion real pendiente.** El evaluador esta implementado, pero `optimizar-contexto` necesita ejecuciones pareadas reales de un proveedor que exponga conteos de tokens; el archivo de ejemplo no constituye evidencia.
- **Medicion agentica negativa inicial.** La captura local usa `GEMINI_API_KEY` solo desde el entorno y guarda resultados ignorados por Git. En el escenario corto de incorporar una Skill externa de stack, `gemini-3.1-flash-lite` uso aproximadamente 20 % mas tokens con `optimizar-contexto` (4.117 frente a 3.431 por repeticion), tres llamadas de lectura frente a una y ninguna variante supero la revision humana. El resultado no aprueba la Skill para ese escenario; una tarea mas larga podra medir si el coste inicial se amortiza.
- **Medicion agentica larga negativa.** En la auditoria de migrar `optimizar-contexto` de core a opcional, tres repeticiones con `gemini-3.1-flash-lite` consumieron 11.163 tokens por tratamiento frente a 8.499 por control: 31,3 % mas, con tres llamadas de herramienta frente a dos. Ninguna respuesta se aprobo: ambas variantes inventaron rutas y comandos inexistentes. La duracion del control quedo contaminada por dos reintentos de cuota en una repeticion, por lo que no se usa como comparacion de rendimiento. La Skill no se considera eficaz ni ahorradora para este escenario.

## 6. Siguiente paso logico

Revisar el diff y ejecutar la CI remota de `0.2.0-alpha.12` antes de publicar. Para seguir la evaluacion de `optimizar-contexto`, fortalecer el evaluador con una rubrica local que rechace rutas y comandos inexistentes antes de plantear un tercer escenario; cualquier redistribucion sigue condicionada por la procedencia de `mobile-flutter`.
