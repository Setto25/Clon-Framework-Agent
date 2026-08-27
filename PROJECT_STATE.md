# Estado del proyecto: agent-framework

**Ultima actualizacion:** 2026-08-27 (rev 21)
**Estado general:** Referencias interoperables depuradas; pilotos y procedencia pendientes
**Fase activa:** Fase 6 — validacion interna previa a pilotos

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
| `backend-fastapi` | fastapi-setup | Creado para el framework (uv, SQLAlchemy, Alembic, pytest) |
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

## 5. Que falta

- **Validacion con proyecto real.** Ningun proyecto ha consumido la plantilla todavia. El primer uso real revelara friccion en el wizard de iniciar-proyecto, gaps en las reglas, y skills que sobran o faltan.
- **Stack backend-fastapi.** Creado con skill `fastapi-setup`. Sin validacion en proyecto real todavia.
- **Procedencia de Skills.** La fuente y licencia deben resolverse antes de cualquier redistribucion. Las correcciones para uso personal quedan permitidas y registradas.
- **Validacion funcional.** La estructura y las invariantes de seguridad estan probadas, pero cada Skill tecnica necesita un escenario piloto que mida si mejora el resultado frente a trabajar sin ella.
- **CI remota.** La matriz Windows/Ubuntu y Python 3.9/3.12 no puede considerarse aprobada hasta ejecutar GitHub Actions; no se publicara solo para obtener esa evidencia.

## 6. Siguiente paso logico

Mientras los pilotos permanezcan pospuestos, continuar la auditoria interna de entradas derivadas y validacion del contrato, priorizando tipos, valores permitidos y mensajes de error recuperables. Ejecutar un piloto real solo cuando el usuario decida crear un proyecto.
