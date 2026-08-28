# Estado del proyecto: agent-framework

**Ultima actualizacion:** 2026-08-28 (rev 49)
**Estado general:** CI aprobada e integrada en main local; uso conversacional y traslado privado mediante GitHub documentados
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
│   └── d_plan_migracion.md
└── plantilla/                ← La plantilla consumible por proyectos nuevos
    ├── AGENTS.md             (template con {{placeholders}})
    ├── PROJECT_STATE.md      (template vacio — NO es el estado de este repo)
    ├── .agents/
    │   ├── skills/
    │   │   ├── cerrar-modulo/
    │   │   ├── evaluar-agente/
    │   │   ├── iniciar-proyecto/
    │   │   ├── lecciones-aprendidas/
    │   │   ├── seguridad-backend/
    │   │   └── stacks/
    │   └── rules/
    │       ├── claude.md
    │       └── excepciones_nominales.md
    ├── documentacion/
    └── opcional/
        └── delegar-entre-agentes/
```

## 3. Stacks disponibles (completos)

| Stack | Skills | Origen |
|---|---|---|
| `backend-fastapi` | fastapi-setup; seguridad-backend como core complementaria | Creado para el framework (uv, SQLAlchemy, Alembic, pytest, OWASP) |
| `firmware-esp32` | desarrollar-firmware, diagnosticar-hardware | Extraido de entrevoces |
| `frontend-nextjs` | nextjs-fullstack, typescript-react | Creado para el framework |
| `ia-llm` | rag-local, fine-tuning-llm, agentes-multiagent | Creado para el framework |
| `mobile-flutter` | flutter-state-management, flutter-performance, flutter-animations | Adaptado de spjoshis/claude-code-plugins (licencia pendiente de verificacion) |

Cada stack tiene LEEME.md con reglas adicionales, terminos tecnicos y procedimiento de instalacion.

## 4. Decisiones vigentes

1. **Stacks por tecnologia, no por dominio.** La reorganizacion packs/ → stacks/ ya se aplico.
2. **Domain-packs como stubs.** No son activables desde iniciar-proyecto. Se materializan manualmente cuando un proyecto los necesite. Ejemplo: `firmware-esp32/domain-packs/audio-embebido/`.
3. **delegar-entre-agentes en opcional/.** Sin evidencia de uso real en entrevoces. Aspiracional, no core.
4. **Candidatos de plugins externos: vetting cerrado.** flutter-development, nodejs-development, rag-cli y custom-plugin-ai-engineer fueron evaluados. Los aprovechables se distribuyeron en los 4 stacks actuales; los descartados no se incluyeron.
5. **Lecciones aprendidas como skill de core**, no como documento suelto. Vive en `.agents/skills/lecciones-aprendidas/` con archivos de referencia por stack.
6. **Superpowers formalizados** en rules/claude.md §2 (brainstorming, TDD, depuracion 4 fases) + §3 (eficiencia de contexto).
7. **Convencion de idioma en 3 categorias** documentada en excepciones_nominales.md. ~20 terminos universales limpios de contaminacion de stack.
8. **Renombrado PROMPT_SISTEMA → SYSTEM_PROMPT** completado, sin roturas de referencias.
9. **Plan de correcciones formalizado.** `ESTADO_CORRECCIONES.md` conserva el avance, las evidencias, los bloqueos y el siguiente paso del endurecimiento hasta `v1.0.0`.
10. **Rama de estabilizacion aislada.** Las correcciones se realizan en `codex/estabilizacion-framework` para preservar el arbol de trabajo preexistente sin resets ni eliminaciones.
11. **Linea base versionada por grupos.** El core y los stacks se registraron en `1aeed87`; el inicializador alfa se registro en `f845050`. La documentacion del meta-repositorio se mantiene separada para facilitar la revision.
12. **Fase 1 completada localmente.** La rama local `main` rastrea `origin/main` y se valido mediante un clon temporal limpio. La rama de estabilizacion contiene correcciones posteriores que se integraran por fast-forward al cerrar la revision. La publicacion remota se difiere hasta cerrar seguridad y licencia.
13. **Licencia externa pendiente de verificacion.** La fuente atribuida al stack `mobile-flutter` no mostro una licencia primaria en el arbol publico revisado; no se asumira MIT para una eventual redistribucion comercial sin evidencia adicional.
14. **Skills congeladas por procedencia.** Por decision del usuario no se modifican, agregan ni eliminan Skills hasta completar el inventario de fuentes, versiones y licencias. Los riesgos se documentan en `ATRIBUCIONES.md`.
15. **Protecciones Git instaladas.** La raiz y `plantilla/` incluyen `.gitignore` y `.gitattributes`; `.env` queda ignorado, `.env.ejemplo` permanece versionable y los archivos de texto principales usan finales LF.
16. **Licencia raiz diferida.** No se aplicara una licencia global hasta separar el contenido original de las adaptaciones con derechos pendientes. La correccion tecnica continua sin tocar Skills.
17. **Contrato unico de placeholders.** `plantilla/configuracion_plantilla.json` declara los campos configurables y `scripts/validar_contrato_plantilla.py` comprueba su uso. Los alias duplicados se eliminaron fuera de Skills.
18. **Limite de congelacion respetado.** El contrato excluye `.agents/skills`; los placeholders operativos de esas rutas no se modifican ni se validan como configuracion inicial.
19. **Inicializador interno reconstruido.** `plantilla/scripts/inicializar_proyecto.py` consume el contrato, protege `.env`, separa nombre visible e identificador tecnico, conserva procedencia y rechaza reinicializaciones.
20. **Inmutabilidad de Skills comprobada.** Una prueba temporal comparo SHA-256 antes y despues de inicializar; todas las Skills permanecieron identicas.
21. **Creacion de un comando verificada.** `scripts/crear_proyecto.py` copia hacia un temporal, instala solamente las Skills autorizadas, ejecuta el inicializador contractual y publica el destino solo al terminar. Rechaza sobrescrituras y conserva byte por byte cada Skill seleccionada.
22. **Wizard alineado con la CLI.** La Skill `iniciar-proyecto` recomienda desde el catalogo, exige confirmacion nominal y delega la instalacion en la CLI Python.
23. **Memoria operativa completa.** La plantilla incorpora plan de desarrollo, documentacion tecnica y guia de operacion. `scripts/verificar_memoria_proyecto.py` comprueba la existencia, el contenido y la ausencia de placeholders configurables pendientes en los documentos obligatorios.
24. **Prueba documental reproducible.** Un proyecto temporal se genero con 14 archivos configurados y cero pendientes; sus siete documentos obligatorios pasaron el verificador y las Skills seleccionadas coincidieron byte por byte con la fuente.
25. **Verificacion estricta de pendientes.** El verificador distingue placeholders sin resolver y marcadores TODO creados por `--permitir-pendientes`; solo una memoria completamente configurada obtiene salida valida.
26. **README alineado con la implementacion.** La guia principal presenta el catalogo, el core automatico, `--skill`, la confirmacion explicita y la copia manual sin filtrado como contingencia.
27. **Fase documental cerrada.** Todos los documentos prometidos existen y el flujo descrito se probo de punta a punta, incluida la seleccion de Skills.
28. **Suite permanente incorporada.** `pruebas/prueba_creacion_proyecto.py` cubre creacion completa, seleccion exacta, nombres desconocidos, pendientes, limpieza tras fallo, rechazo de sobrescritura, proteccion de `.env` e inmutabilidad del contenido seleccionado con `unittest`.
29. **Matriz de CI definida.** `.github/workflows/validacion.yml` ejecuta el contrato y la suite en Windows y Ubuntu con Python 3.9 y 3.12. Su aprobacion remota queda pendiente hasta publicar la rama y ejecutar GitHub Actions.
30. **Skills seleccionadas preservadas por prueba.** La suite calcula y compara SHA-256 de cada Skill copiada; el inventario separado controla todo el catalogo fuente.
31. **Reproducibilidad desde Git comprobada.** Se creo un clon temporal limpio del commit `864ba88`; el contrato y las cuatro pruebas aprobaron fuera del arbol de trabajo. El clon se elimino despues de la comprobacion.
32. **Integracion local lineal.** Se comprobo que `main` era ancestro directo de `codex/estabilizacion-framework`, con siete commits adicionales y sin cambios de Skills respecto de `main`. La rama local `main` se adelanto por fast-forward sin eliminar ramas ni publicar cambios.
33. **Inventario congelado reproducible.** `scripts/inventariar_skills.py` registra 32 archivos, 17 manifiestos `SKILL.md`, tamaños, SHA-256 y declaraciones locales de procedencia en `auditoria/inventario_skills.json`. Una quinta prueba impide que el inventario quede desactualizado.
34. **Declaracion local insuficiente.** El analisis mecanico detecto una sola declaracion explicita de procedencia, en `mobile-flutter`; afirma MIT, pero esa afirmacion continua sin evidencia primaria verificada.
35. **Modificacion autorizada para uso personal.** El usuario autorizo mejorar las Skills sin eliminarlas. La restriccion anterior de congelacion queda reemplazada por una politica de cambios probados, inventariados y sin redistribucion mientras la procedencia siga incompleta.
36. **Skills criticas reconstruidas.** `iniciar-proyecto` ahora delega en la CLI Python, no duplica placeholders y no mueve ni borra Skills. `agentes-multiagent` prioriza soluciones simples, autorizacion externa al modelo, aislamiento real y evaluaciones adversariales.
37. **Guias tecnicas endurecidas.** FastAPI exige secretos sin valor predeterminado y lock validado; Next.js usa cache explicita; RAG y fine-tuning eliminan precios, modelos, VRAM y umbrales universales. Los nombres de negocio leen el idioma desde `AGENTS.md` en vez de placeholders no procesados.
38. **Validacion estructural completa.** Las 17 Skills aprobaron `quick_validate.py`. La suite controla cantidad, frontmatter, inventario, copia byte por byte y ausencia de instrucciones obsoletas o destructivas.
39. **Catalogo fuente separado de la instancia.** `scripts/catalogo_skills.py` descubre y clasifica las 17 Skills mediante `TypedDict`; ninguna se elimina de `plantilla/`.
40. **Core automatico minimo.** Todo proyecto generado recibe exactamente `cerrar-modulo`, `lecciones-aprendidas` y `probar-e2e`. Las restantes se instalan solo mediante argumentos repetibles `--skill NOMBRE`.
41. **Recomendacion sin autorizacion implicita.** El agente puede proponer Skills a partir del objetivo, stack y hardware confirmados, pero debe obtener confirmacion de nombres exactos antes de agregarlas al comando.
42. **Trazabilidad de instancia.** `.estado-plantilla.json` registra la lista descubierta de Skills instaladas y la politica aplicada. Los `LEEME.md` de stacks ya no instruyen movimientos manuales.
43. **Selector probado localmente.** Python 3, `argparse`, `pathlib`, `shutil`, `TypedDict` y `unittest` sostienen el flujo. Las 17 Skills, el contrato y 14 pruebas aprobaron el 2026-08-27.
44. **Inicializacion unica.** `inicializar_proyecto.sh` quedo reducido a un adaptador que delega argumentos en Python; ya no genera catalogos alternativos ni sugiere movimientos manuales.
45. **Selector versionado localmente.** El cambio funcional se registro en `1153a6f`; `main` local lo contiene sin publicar en `origin` ni eliminar ramas.
46. **Capacidades verificables por agente.** Los deltas de Antigravity, Claude y Codex ya no atribuyen acceso, descubrimiento o proveedor por suposicion; cada sesion comprueba herramientas, sandbox y permisos observables.
47. **Referencia inexistente eliminada.** Se retiro `.agents/rules/{{NOMBRE_PROYECTO}}_contexto.md`, que nunca formo parte de la plantilla, y una prueba impide reintroducirla junto con afirmaciones obsoletas.
48. **Nombre seguro para dotenv.** El contrato `2` y la version `0.2.0-alpha.2` derivan `NOMBRE_PROYECTO_ENV` mediante JSON, limitan nombre e idioma y rechazan caracteres de control antes de escribir.
49. **Historial limpio por proyecto.** `REGISTRO_CAMBIOS.md` dejo de heredar decisiones internas de `agent-framework`; ahora registra fecha, version de origen, Skills instaladas y siguiente paso de la instancia.
50. **Regresion ampliada.** La suite tiene 19 pruebas e incluye referencias comunes, capacidades obsoletas, escape dotenv, rechazo de saltos de linea y memoria inicial propia.
51. **Inventario independiente de plataforma.** La exportacion limpia detecto que las huellas variaban entre CRLF y LF. El inventario version `2` canoniza texto UTF-8 a LF y una prueba compara ambos formatos.
52. **Exportacion limpia aprobada.** Los commits `ac08dab` y `62d3db3` contienen el endurecimiento y la normalizacion. Un `git archive` de `HEAD` aprobo el contrato y las 19 pruebas sin depender del arbol de trabajo; los temporales se eliminaron.
53. **Validacion previa a toda escritura.** `preparar_cambios` rechaza valores que reintroduzcan sintaxis `{{PLACEHOLDER}}` antes de crear Git o modificar archivos.
54. **Inicializacion directa transaccional.** La version `0.2.0-alpha.3` respalda archivos, conserva el centinela y revierte estado, `.env`, directorios y `.git` creados por una ejecucion fallida.
55. **Atomicidad comprobada.** La suite tiene 22 pruebas. Una copia manual con placeholder ambiguo permanecio byte por byte intacta; otra con `.env` desprotegido revirtio el `git init`; un fallo deliberado posterior a la escritura restauro archivos, `.env`, Git y `.plantilla-framework`.
56. **Exportacion transaccional aprobada.** El commit `c7e76b3` aprobo el contrato y las 22 pruebas desde un `git archive` limpio; la copia temporal y su archivo comprimido se eliminaron despues de la validacion.
57. **Convenciones sin proveedor supuesto.** `AGENTS.md`, `PROJECT_STATE.md`, `.agents/`, `SKILL.md` y `.env` se documentan como interfaces reservadas por herramientas o por el contrato del framework. Cada agente comprueba su descubrimiento real y carga manualmente lo que falte.
58. **Referencia arqueologica eliminada.** El indice de una instancia ya no apunta a `documentacion/analisis/`, ruta historica que solo existe en el meta-repositorio.
59. **Referencias condicionales comprobadas.** La version `0.2.0-alpha.4` y 23 pruebas verifican que cada stack citado tenga `LEEME.md` y referencia de lecciones, y que las Skills condicionales del indice existan en la fuente.
60. **Exportacion agnostica aprobada.** El commit `91346e6` aprobo el contrato y las 23 pruebas desde un `git archive` limpio; los temporales se eliminaron al finalizar.
61. **Contrato ejecutable estricto.** La version `0.2.0-alpha.5` acepta solamente contrato version `2`, sintaxis `{{CLAVE}}`, origenes conocidos, claves exactas y rutas relativas portables sin duplicados.
62. **Precedencia ambigua eliminada.** Una clave no puede repetirse entre JSON, argumentos posicionales o `--valor`; los campos derivados se calculan internamente y no aceptan suplantacion externa.
63. **Texto de configuracion endurecido.** Los saltos multilinea y tabulaciones legitimos se conservan, mientras controles Unicode invisibles y listas con elementos multilinea se rechazan antes de escribir.
64. **Regresion de entradas ampliada.** La suite tiene 28 pruebas e incluye contratos futuros o deformados, valores derivados externos, duplicados entre fuentes y controles Unicode.
65. **Exportacion contractual aprobada.** El commit `dfb20d7` aprobo el contrato y las 28 pruebas desde un `git archive` limpio; la copia y el archivo temporal se eliminaron al finalizar.
66. **Arboles locales regulares.** La version `0.2.0-alpha.6` rechaza enlaces simbolicos, junctions, reparse points y cambios de dispositivo dentro de la plantilla fuente o de una copia manual antes de leer el contrato o copiar archivos.
67. **Destino lexico y resuelto protegido.** El creador comprueba tanto la ruta escrita por el usuario como su resolucion real. Un destino que existe como enlace roto se considera ocupado y no se sigue ni reemplaza.
68. **Regresion de enlaces comprobada.** La suite tiene 30 pruebas. Los dos casos de enlace se ejecutaron en Windows sin omisiones: el archivo externo permanecio intacto y el destino roto no creo su objetivo.
69. **Exportacion de rutas aprobada.** El commit `6214737` aprobo el contrato y las 30 pruebas desde un `git archive` limpio; los enlaces adversariales se probaron de nuevo y los temporales se eliminaron.
70. **Residuos locales excluidos.** Se retiro `plantilla/scripts/__pycache__/`, artefacto ignorado por Git que `copytree` podia incorporar. Cachés, bytecode y archivos especiales ahora provocan un error antes de copiar o inicializar.
71. **Recursos con limites generosos.** La version `0.2.0-alpha.7` limita cada arbol a 20 000 entradas, 100 MiB totales y 20 MiB por archivo; cada JSON a 1 MiB y cada valor a 100 000 caracteres.
72. **Permisos controlados.** El temporal publicado conserva contenido y ejecutabilidad, elimina bits especiales y garantiza lectura y escritura del propietario. Una copia manual con archivos administrados de solo lectura falla antes de crear Git.
73. **Publicacion revalidada.** El destino se comprueba inmediatamente antes de `os.replace`; si aparecio durante la creacion se conserva y el temporal propio se elimina. La proteccion es de mejor esfuerzo ante una carrera hostil ocurrida entre esa comprobacion y la llamada atomica.
74. **Operaciones con tiempo finito.** Cada comando Git dispone de 30 segundos y el inicializador invocado por el creador de 120 segundos. La suite tiene 38 pruebas y cubre limites acumulados, JSON, valores, permisos, caché y publicacion tardia.
75. **Exportacion de recursos aprobada.** El commit `534e906` aprobo el contrato y las 38 pruebas desde un `git archive` limpio; los temporales de la exportacion y de los escenarios adversariales se eliminaron.
76. **Piso Python corregido y vigilado.** La version `0.2.0-alpha.8` evita `Path.write_text(newline=)`, API posterior a Python 3.9, y analiza todos los modulos con la gramatica 3.9. La ejecucion real en ese interprete continua pendiente de la matriz remota porque el entorno local solo dispone de Python 3.13.
77. **Validaciones duplicadas bajo contrato.** La autonomia de la copia exige conservar validaciones tanto en el meta-repositorio como en `plantilla/`; una prueba AST compara versiones, claves, origenes, limites y artefactos rechazados para impedir divergencias silenciosas.
78. **Git preexistente delimitado.** El inicializador directo admite repositorios limpios con historial y repositorios sin primer commit. Rechaza cambios rastreados o preparados, repositorios invalidos y operaciones merge, rebase, cherry-pick, revert o bisect activas sin eliminar `.git` ni modificar la copia.
79. **Exportacion de compatibilidad aprobada.** El commit `08b0b41` aprobo el contrato y las 44 pruebas desde un `git archive` limpio. El archivo y el directorio temporales se eliminaron al finalizar; la auditoria local previa a pilotos queda cerrada.
80. **Primer piloto iniciado.** Se genero `D:\PROYECTOS\piloto-inventario-api` mediante la CLI con el core automatico y `fastapi-setup`. Su modulo inicial implementa configuracion tipada, salud y productos en memoria con cinco pruebas aprobadas y un recorrido E2E local aprobado. El piloto no se considera cerrado: SQLite y la revision de la advertencia de TestClient son el siguiente hito.
81. **Seguridad backend como core seleccionable.** `seguridad-backend` modela actores, limites de confianza, autorizacion por funcion, objeto y propiedad, controles por riesgo, pruebas negativas y puerta de exposicion. Permanece fuera del core automatico para no contaminar proyectos sin backend; `iniciar-proyecto` la recomienda cuando una API se expone a red o procesa identidades y datos sensibles.
82. **Version de plantilla `0.2.0-alpha.9`.** El catalogo contiene 18 Skills y 35 archivos inventariados. La nueva Skill y sus referencias se copian byte por byte mediante `--skill seguridad-backend`; el core automatico conserva exactamente tres Skills.
83. **Instalacion posterior transaccional.** `scripts/agregar_skills.py` permite incorporar una Skill confirmada a un proyecto inicializado sin reinicializarlo. Verifica el estado y el arbol de Skills, prepara la copia en un temporal, conserva las Skills existentes y actualiza `.estado-plantilla.json` de forma atomica. Las pruebas cubren la incorporacion byte por byte y el rechazo de duplicados.
84. **Primer piloto endurecido.** `D:\PROYECTOS\piloto-inventario-api` incorporo `seguridad-backend`; la entrada de productos rechaza propiedades no autorizadas y nombres vacios tras normalizacion. La revision aprueba exclusivamente el servicio local, sin declarar listos autenticacion, autorizacion, TLS, CORS ni limites de red.
85. **Version de plantilla `0.2.0-alpha.10`.** El instalador posterior formaliza la seleccion confirmada para proyectos que ya existian al agregar una nueva Skill.
86. **Persistencia PostgreSQL validada en el primer piloto.** `D:\PROYECTOS\piloto-inventario-api` incorporo SQLAlchemy, Alembic y psycopg, aplico la migracion inicial a PostgreSQL 18 local y verifico por HTTP la creacion y lectura de un producto, eliminando despues el dato temporal. SQLite se conserva solo para aislar las pruebas; no sustituye la integracion real.
87. **Primer piloto cerrado.** El MVP local del piloto FastAPI tiene evidencia de pruebas, migracion, recorrido HTTP, memoria y guia de operacion. Registro una leccion concreta sobre ACL de Windows entre identidades de ejecucion; autenticacion, autorizacion y exposicion siguen fuera del alcance confirmado y no se declaran cubiertas.
88. **Segundo piloto cerrado.** `D:\PROYECTOS\piloto-inventario-web` valido `nextjs-fullstack` y `typescript-react` con Next.js 16.3.3, pruebas, lint, build y un recorrido HTTP repetido contra el piloto FastAPI local. La memoria no conserva pendientes de inicializacion.
89. **Fricciones de pilotos sintetizadas.** `auditoria/sintesis_pilotos.md` registra la evidencia de los dos pilotos y prioriza tres mejoras: tratamiento reproducible de texto multilinea en PowerShell, validacion automatizada del frontend anidado y convencion documental para `interfaz/`. Las ACL de Windows y PostgreSQL local se delimitan como precondiciones de entorno, no como defectos funcionales de las Skills.
90. **Flujos de pilotos endurecidos.** El inicializador rechaza la secuencia literal `` `n`` o `` `r`` en `--valor` y exige configuracion JSON para texto multilinea, con regresion de creacion. `scripts/validar_frontend_nextjs.py` valida `interfaz/package.json` y ejecuta `test`, `lint` y `build` con `npm.cmd` en Windows. La ejecucion elevada contra el piloto real detecto una ACL de `.env.local`; no se alteraron permisos ni secretos.
91. **Segundo piloto validado de forma reproducible.** Tras restaurar ACL heredadas en el entorno local, `D:\PROYECTOS\piloto-inventario-web\interfaz` aprobo `npm run test` (2 pruebas), `npm run lint` y `npm run build` mediante el validador del framework. `vitest.config.mts` evita que las pruebas aisladas carguen `.env.local`; el aviso de compatibilidad de Vite quedo eliminado.
92. **Rama de estabilizacion publicada.** El commit `bf56889` se publico en `origin/codex/estabilizacion-framework` sin modificar `origin/main`, activando la matriz de GitHub Actions. La API del repositorio requiere autenticacion para consultar sus ejecuciones desde esta sesion; la conclusion remota debe verificarse en GitHub antes de declarar aprobada la CI.
93. **Inventario de CI aislado de la copia de trabajo.** La primera ejecucion remota detecto una divergencia de huellas entre la copia del runner y el inventario versionado. `prueba_inventario_skills.py` ahora extrae las Skills desde `git archive HEAD` hacia un temporal controlado antes de compararlas, mientras conserva la regresion LF/CRLF. La prueba verifica asi el contenido publicado y no atributos locales del checkout.
94. **Diagnostico remoto acotado.** La segunda ejecucion fallo tambien en Ubuntu/Python 3.12 pese a que clonaciones frescas y archivos Git locales coinciden. La CI registra ahora el commit, el inventario calculado y el inventario esperado antes de la suite para identificar la divergencia sin desactivar la comprobacion.
95. **Orden de inventario independiente de plataforma.** La traza remota mostro archivos individuales identicos y una huella conjunta distinta. La causa fue ordenar objetos `Path`, cuya comparacion depende de la plataforma. `inventariar_skills.py` ordena ahora por rutas POSIX textuales y una regresion cubre mayusculas; se regenero el inventario y se retiro la traza temporal de CI.
96. **Padres temporales normalizados.** El creador resuelve el padre esperado antes de comparar la ubicacion del temporal, evitando un rechazo falso de Windows sin aceptar rutas fuera del directorio controlado. La extraccion de inventario en pruebas declara el directorio seguro solo para su propio proceso Git, sin alterar la configuracion global.
97. **CI aprobada y licencia no verificable.** La matriz remota aprobo Windows y Ubuntu con Python 3.9 y 3.12. La revision focalizada confirmo la fuente Flutter y sus tres Skills, pero no encontro licencia aplicable ni revision de origen identificada; el marco se conserva para uso privado sin redistribucion.
98. **Integracion local cerrada.** `main` se adelanto por fast-forward hasta `8bf5dbc`, que incorpora la estabilizacion validada y la auditoria privada. `origin/main` no se modifico; la rama remota de estabilizacion conserva el ultimo commit publicado de CI.
99. **README alineado con evidencia.** La guia de uso ya declara los dos pilotos privados y la matriz de CI aprobada. Distingue las garantias tecnicas comprobadas de la procedencia externa pendiente, que solo limita una futura redistribucion.
100. **Entrada conversacional formalizada.** `iniciar-proyecto` convierte la frase de inicio desde un IDE en una entrevista breve, recomendacion explicada, confirmacion de destino y Skills, y ejecucion de la CLI ya validada. No crea archivos antes de esa confirmacion y conserva la ruta manual como alternativa reproducible.
101. **Uso entre computadores documentado.** El README separa la publicacion consciente del framework, su clonacion en otro PC y la creacion de proyectos consumidores como repositorios hermanos. `git pull --ff-only` actualiza solo el meta-repositorio; las instancias no se modifican implicitamente.

## 5. Que falta

- **Validacion con proyecto real.** Dos pilotos independientes completaron sus flujos locales, sus fricciones fueron sintetizadas y el validador frontend se ejecuto de extremo a extremo. Falta validar en CI remota.
- **Stack backend-fastapi.** El piloto uso `fastapi-setup` y valido setup, configuracion tipada, rutas, esquemas, servicio, migraciones, persistencia PostgreSQL y pruebas. Quedan autenticacion y autorizacion fuera de alcance hasta confirmar actores y exposicion.
- **Procedencia de Skills.** La fuente y licencia deben resolverse antes de cualquier redistribucion. Las correcciones para uso personal quedan permitidas y registradas.
- **Validacion funcional.** La estructura y las invariantes de seguridad estan probadas, pero cada Skill tecnica necesita un escenario piloto que mida si mejora el resultado frente a trabajar sin ella.
- **CI remota.** La matriz aprobo Windows y Ubuntu con Python 3.9 y 3.12 en la rama de estabilizacion.

## 6. Siguiente paso logico

Usar `main` local como linea validada para instanciar proyectos privados. Si en el futuro se desea redistribuir, primero identificar el commit de origen o conseguir autorizacion del autor para `mobile-flutter`. Toda exposicion futura requiere definir actores, autenticacion y autorizacion.
