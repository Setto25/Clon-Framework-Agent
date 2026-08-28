# Estado de correcciones de agent-framework

**Ultima actualizacion:** 2026-08-28 (rev 46)
**Estado general:** CI aprobada e integrada en main local; uso conversacional y traslado privado mediante GitHub documentados
**Fase activa:** Fase 7 — cierre de validacion local y preparacion de CI
**Rama de trabajo:** `main` local; `codex/estabilizacion-framework` se conserva como historial de estabilizacion

## 1. Proposito

Este archivo conserva la memoria operativa del plan de correcciones del framework. Registra el avance, las decisiones, la evidencia, los bloqueos y el siguiente paso para que otra sesion pueda continuar sin reconstruir el contexto.

`PROJECT_STATE.md` mantiene el estado general y arquitectonico del framework. Este archivo mantiene exclusivamente el avance del endurecimiento previo a la primera version estable.

## 2. Objetivo de calidad

El framework debe llegar a una version `v1.0.0` que cumpla estas condiciones:

1. un clon limpio genera un proyecto completo mediante un solo comando;
2. no quedan placeholders de inicializacion sin resolver;
3. ningun secreto queda expuesto o preparado para commit;
4. todas las rutas y los documentos referenciados existen;
5. solo se instalan los stacks y Skills seleccionados;
6. las pruebas automaticas pasan en los sistemas soportados;
7. la documentacion coincide con el comportamiento comprobado;
8. al menos dos proyectos piloto completan el flujo de inicio y cierre.

## 3. Reglas de trabajo

- Se preserva todo cambio preexistente hasta identificar su origen y finalidad.
- No se ejecutan resets, eliminaciones ni reescrituras de historial para normalizar Git.
- Cada fase debe terminar con evidencia verificable y un siguiente paso concreto.
- El inicializador Python sera la unica implementacion de la logica de instalacion.
- La Skill `iniciar-proyecto` actuara como interfaz conversacional del inicializador y no duplicara su logica.
- `AGENTS.md` sera el contrato comun; los deltas por agente solo contendran diferencias comprobadas.
- Los cambios materiales deben actualizar este archivo y `PROJECT_STATE.md`.
- Las Skills pueden corregirse para uso personal con autorizacion del usuario, sin eliminarlas, preservando procedencia, inventario y pruebas. No se redistribuyen mientras su licencia siga pendiente.

## 4. Plan y avance

| Fase | Alcance | Estado | Criterio de salida |
|---|---|---|---|
| 1 | Estabilizar Git y definir la linea base | Completada | Rama canónica definida, arbol limpio y clon reproducible |
| 2 | Seguridad, `.gitignore`, licencia y atribuciones | En curso — procedencia | `.env` protegido, licencia y atribuciones completas |
| 3 | Contrato unico de plantilla y placeholders | Completada | Manifiesto valido y placeholders sin duplicidad |
| 4 | Reconstruir el inicializador | Completada | Un comando genera un proyecto completo y seguro |
| 5 | Corregir wizard, documentos y referencias | Completada — CLI soportada | No existen archivos o rutas prometidas ausentes |
| 6 | Validar Skills, stacks y agentes | Cerrada localmente — dos pilotos sintetizados | Selector, Skills evaluadas y recorridos locales comprobados |
| 7 | Incorporar pruebas y CI | En curso — local aprobada | Matriz automatica aprobada en plataformas soportadas |
| 8 | Ejecutar pilotos y publicar `v1.0.0` | Pendiente | CI remota aprobada, procedencia resuelta y release reproducible |

## 5. Linea base Git observada

Al iniciar las correcciones se encontro:

- rama local activa original: `master`;
- commit local: `4f958a6` (`pre add skills`);
- rama remota registrada: `origin/main`;
- commit remoto registrado: `831e1a6` (`init: framework agentico alfa`);
- la rama local contenia un commit adicional respecto de `origin/main`;
- existian archivos modificados y modulos completos sin versionar;
- el directorio `_dryrun2/` estaba sin versionar y pendiente de clasificacion.

Para preservar el arbol sin alterar contenido se creo la rama `codex/estabilizacion-framework` desde `4f958a6`. Todos los cambios que ya estaban en el arbol permanecieron intactos.

### Clasificacion del arbol pendiente

| Grupo | Contenido | Tratamiento previsto |
|---|---|---|
| Meta-repositorio | `AGENTS.md`, `README.md`, `PROJECT_STATE.md`, `ESTADO_CORRECCIONES.md` | Se versiona como documentacion y memoria real del framework |
| Core consumible | Reglas, Skills core, indice de lectura y registro bajo `plantilla/` | Se revisa y versiona como base comun de todo proyecto generado |
| Stacks consumibles | `backend-fastapi`, `frontend-nextjs`, `ia-llm`, `mobile-flutter` y sus Skills | Se versiona por stack para conservar autoria y facilitar revision independiente |
| Inicializacion | `plantilla/scripts/inicializar_proyecto.py` y respaldo Bash | Se captura como implementacion alfa antes de reconstruirlo en la Fase 4 |
| Evidencia temporal | `_dryrun2/` | Eliminada con autorizacion del usuario despues de registrar el defecto observado |

La clasificacion confirmo que `_dryrun2/` era una salida generada para `proyecto-prueba`. Contenia un repositorio Git interno, un catalogo generado y placeholders sin resolver en `.env`; por ello no pertenecia a la distribucion. El usuario autorizo su eliminacion despues de registrar esa evidencia en este archivo.

## 6. Hallazgos que debe resolver el plan

### Criticos

- La version visible desde la referencia remota no contiene todo el trabajo local.
- El wizard y `PROJECT_STATE.md` utilizan vocabularios de placeholders diferentes.
- El inicializador no procesa `.env.ejemplo` porque su filtro de extensiones lo excluye.
- La plantilla no incluye `.gitignore`, aunque el inicializador crea `.env`.
- El verificador de placeholders mezcla configuracion inicial con ejemplos operativos.

### Altos

- Se referencian documentos que no existen en la plantilla.
- `cerrar-modulo` invoca `scripts/verificar_memoria_proyecto.py`, que no existe.
- Las rutas documentadas para activar stacks no coinciden con la estructura real.
- El wizard prioriza el inicializador Bash aunque el README declara Python como recomendado.
- La compatibilidad declarada por agente contiene afirmaciones contradictorias o no verificadas.

### Medios

- El README contiene inventarios contradictorios.
- El proyecto generado no conserva la version exacta del framework de origen.
- La plantilla hereda historial interno del framework.
- Falta una licencia raiz y una atribucion formal del contenido adaptado.
- No existe una suite automatica que demuestre una instalacion reproducible.

## 7. Registro de avance

### 2026-08-28 — Rev 34

**Completado:**

- Se creo y cerro `D:\PROYECTOS\piloto-inventario-web` con las Skills confirmadas `nextjs-fullstack` y `typescript-react`.
- Next.js 16.3.3 aprobo dos pruebas Vitest, lint, build y recorrido HTTP repetido contra FastAPI local.

**Resultado:**

Los dos pilotos locales requeridos por el plan ya existen y completaron su flujo. Permanecen pendientes la CI remota, la procedencia/licencia para redistribucion y la sintesis de fricciones antes de proponer una release.

### 2026-08-28 — Rev 35

**Completado:**

- El inicializador rechaza secuencias literales `` `n`` y `` `r`` de PowerShell en `--valor`, y dirige el texto multilinea hacia `--configuracion` JSON.
- Se creo `scripts/validar_frontend_nextjs.py`, que exige los scripts `test`, `lint` y `build` en `interfaz/package.json` y los ejecuta desde ese subdirectorio con la variante correcta de npm para Windows.

**Evidencia:**

- La regresion de creacion, dos pruebas estructurales del validador, el contrato y la suite completa aprobaron localmente.
- La ejecucion elevada contra el piloto real alcanzo Vitest, pero fue rechazada al abrir `interfaz/.env.local` por una ACL entre identidades. No se cambiaron permisos ni secretos.

**Resultado:**

La friccion de texto multilinea queda corregida. El validador frontend queda disponible y falta repetir su recorrido completo bajo una identidad con acceso local al entorno antes de promover CI remota.

### 2026-08-28 — Rev 36

**Completado:**

- Se renombro la configuracion de Vitest a `vitest.config.mts`, eliminando el aviso de compatibilidad de Vite.
- El validador reproducible ejecuto contra el piloto real `npm run test`, `npm run lint` y `npm run build` desde `interfaz/`.

**Evidencia:**

- Vitest aprobo 2 pruebas.
- ESLint y el build de produccion de Next.js 16.3.3 aprobaron.

**Resultado:**

Los dos pilotos locales requeridos completaron su cierre tecnico. Solo permanecen la revision de cambios, la CI remota y la procedencia/licencia previa a una redistribucion.

### 2026-08-28 — Rev 37

**Completado:**

- Se publico `codex/estabilizacion-framework` en `origin` hasta el commit `bf56889`, sin modificar `origin/main`.

**Resultado:**

La matriz de GitHub Actions queda solicitada por el evento `push`. La API del repositorio devolvio `404` sin autenticacion desde esta sesion, por lo que su conclusion debe comprobarse en la interfaz de GitHub antes de cerrar la CI.

### 2026-08-28 — Rev 38

**Completado:**

- Se corrigio `prueba_inventario_skills.py` para calcular la huella sobre `git archive HEAD` en un temporal controlado, en lugar de depender de atributos de la copia de trabajo del runner.

**Evidencia:**

- La regresion de inventario, el contrato y las 50 pruebas aprobaron localmente.
- Un clon fresco de la rama remota y un archivo Git local generaron la misma huella inventariada.

**Resultado:**

Se publica una ejecucion correctiva de la matriz remota. La conclusion de GitHub Actions sigue siendo el criterio pendiente para cerrar la CI.

### 2026-08-28 — Rev 39

**Completado:**

- Se agrego una traza acotada a la CI que muestra el commit descargado, el inventario calculado y el inventario registrado antes de la suite.

**Resultado:**

La segunda ejecucion fallo en Ubuntu/Python 3.12 con una huella inesperada pese a reproducirse correctamente en clonaciones frescas. La siguiente ejecucion entregara la evidencia necesaria para corregir sin relajar la invariabilidad del inventario.

### 2026-08-28 — Rev 40

**Completado:**

- Se identifico que los 35 archivos individuales coincidian y que solo variaba la huella conjunta.
- `inventariar_skills.py` ordena ahora por rutas POSIX textuales en vez de comparar objetos `Path` dependientes de la plataforma.
- Se regenero el inventario, se agrego la regresion de orden y se retiro la traza temporal de la CI.

**Evidencia:**

- La regresion de inventario aprobo tres pruebas.
- El contrato y la suite completa aprobaron 51 pruebas localmente.

**Resultado:**

Se publica la correccion final para una nueva ejecucion de CI remota. La conclusion de GitHub Actions sigue siendo el criterio pendiente antes de declarar la matriz aprobada.

### 2026-08-28 — Rev 41

**Completado:**

- Se identifico que Windows resolvia el padre del temporal con una representacion distinta de la ruta recibida por el creador.
- `crear_proyecto.py` resuelve ambos lados antes de validar el padre y mantiene el requisito de que el temporal pertenezca al directorio controlado.
- Se amplio la regresion de publicacion tardia con un padre expresado lexicalmente.
- La prueba de inventario declara `safe.directory` solo en su proceso Git para funcionar bajo identidades de ejecucion distintas, sin modificar configuracion global.

**Evidencia:**

- El contrato de plantilla aprobo.
- La suite completa aprobo 51 pruebas localmente.

**Resultado:**

Ubuntu aprobo la correccion anterior. Se prepara una nueva ejecucion para confirmar los dos trabajos de Windows antes de cerrar la matriz.

### 2026-08-28 — Rev 42

**Completado:**

- La matriz remota aprobo Windows y Ubuntu con Python 3.9 y 3.12 para `fa50664`.
- Se audito la procedencia declarada de `mobile-flutter` sin modificar Skills ni preparar redistribucion.
- La fuente publica confirma el plugin `flutter-development` y las tres Skills relacionadas, pero no aporta una licencia accesible ni la revision exacta que originaria la adaptacion.

**Resultado:**

El framework queda validado para uso privado. La licencia de `mobile-flutter` se registra como no verificable y no es necesario resolverla mientras no se pretenda redistribuir.

### 2026-08-28 — Rev 43

**Completado:**

- `main` se adelanto por fast-forward hasta `8bf5dbc`.
- La integracion incorpora la matriz de CI aprobada y la auditoria de procedencia privada.
- No se envio ningun commit a `origin/main`.

**Resultado:**

`main` local es la linea validada para uso privado; el remoto se conserva sin publicar esta integracion.

### 2026-08-28 — Rev 44

**Completado:**

- Se corrigieron las afirmaciones obsoletas del README sobre pilotos y la matriz de CI.
- La guia ahora diferencia las protecciones tecnicas comprobadas de la procedencia externa que solo condiciona una redistribucion futura.

**Resultado:**

La documentacion de uso coincide con el estado real de `main` local y puede orientar la creacion de proyectos privados.

### 2026-08-28 — Rev 45

**Completado:**

- `iniciar-proyecto` formaliza la entrada conversacional desde un IDE con las preguntas necesarias, recomendacion de Skills y confirmacion previa a la escritura.
- El README documenta el mensaje de inicio y como adjuntar el contexto cuando un IDE no descubre Skills automaticamente.

**Resultado:**

Una persona puede pedir al agente que use el framework sin preparar JSON ni comandos; la CLI segura sigue siendo la unica via que crea la instancia.

### 2026-08-28 — Rev 46

**Completado:**

- El README documenta como publicar conscientemente el framework, clonarlo en otro PC y mantenerlo separado de los proyectos consumidores.
- La actualizacion remota usa `git pull --ff-only` y aclara que las instancias existentes no reciben cambios implicitos.

**Resultado:**

El traslado privado mediante GitHub queda explicado sin ejecutar ninguna publicacion como parte de esta revision.

### 2026-08-28 — Rev 33

**Completado:**

- Se cerro el MVP local del primer piloto despues de revisar pruebas, migracion, recorrido HTTP, guia de operacion y memoria.
- La instancia registro una leccion de entorno sobre ACL de Windows entre identidades de ejecucion, tras varios intentos fallidos de acceso a archivos nuevos.

**Evidencia:**

- El piloto mantuvo 7 pruebas aprobadas, la revision Alembic `20260828_01 (head)` y memoria valida.
- La API no quedo en ejecucion despues de la comprobacion local.

**Resultado:**

El primer piloto satisface el criterio de cierre local para FastAPI y PostgreSQL. La advertencia deprecada de TestClient queda como deuda; autenticacion, autorizacion y exposicion siguen intencionalmente fuera de alcance. El siguiente hito es un segundo piloto independiente.

### 2026-08-28 — Rev 32

**Completado:**

- El primer piloto reemplazo el almacenamiento en memoria por SQLAlchemy, Alembic y psycopg, con PostgreSQL como persistencia objetivo.
- Se aplico la migracion `20260828_01` a PostgreSQL 18 local y un recorrido HTTP en `127.0.0.1` comprobó alta y lectura de productos contra esa instancia; el dato temporal se elimino al finalizar.
- SQLite queda limitado a fixtures aislados de pruebas, mientras la persistencia real se verifica contra PostgreSQL.

**Evidencia:**

- `uv run --no-sync pytest -q` aprobo 7 pruebas; continua una advertencia deprecada externa de Starlette TestClient.
- `uv run --no-sync alembic current` devolvio `20260828_01 (head)`.
- `python scripts/verificar_memoria_proyecto.py . --json` valido la memoria del piloto.

**Resultado:**

El primer piloto valida la Skill `fastapi-setup` junto a la persistencia PostgreSQL y la puerta local de `seguridad-backend`. Autenticacion, autorizacion y exposicion permanecen fuera de su alcance; el siguiente criterio del framework es registrar las fricciones del cierre e iniciar un segundo piloto.

### 2026-08-28 — Rev 31

**Completado:**

- Se creo `scripts/agregar_skills.py` para incorporar Skills confirmadas en una instancia inicializada sin reinicializarla.
- El comando valida el estado registrado, las Skills instaladas y los enlaces; prepara la copia en un temporal y actualiza el estado solo despues de publicar rutas nuevas.
- El primer piloto instalo `seguridad-backend` con el nuevo comando, documento su matriz local y endurecio el schema de productos contra propiedades no autorizadas y nombres vacios.
- La revision no agrega controles que no corresponden al alcance confirmado: el piloto sigue aprobado solo para `127.0.0.1` y sin usuarios ni datos sensibles.
- El framework avanzo a `0.2.0-alpha.10`.

**Evidencia:**

- La suite valida instalacion posterior byte por byte y rechazo de una Skill duplicada.
- Las 47 pruebas automaticas aprobaron, incluida la incorporacion de varias Skills del mismo stack.
- La revision del piloto aprobo 7 pruebas y su memoria valida sin placeholders ni pendientes de inicializacion.

**Resultado:**

La nueva Skill puede evaluarse en un piloto ya existente sin contradecir la politica de seleccion explicita. Ese piloto luego valido persistencia PostgreSQL; autenticacion y exposicion siguen fuera de alcance hasta contar con requisitos concretos.

### 2026-08-28 — Rev 30

**Completado:**

- Se creo `seguridad-backend` como Skill core seleccionable, con referencias separadas para controles generales y FastAPI.
- La Skill exige alcance, limites de confianza, matriz por endpoint, controles proporcionales, pruebas negativas y evidencia antes de recomendar exposicion.
- Se consultaron OWASP ASVS 5.0.0, OWASP API Security Top 10 2023, OWASP REST Security Cheat Sheet y documentacion oficial de FastAPI; la redaccion local es original y las fuentes quedaron atribuidas.
- `iniciar-proyecto` recomienda la Skill para backends expuestos o sensibles sin instalarla implicitamente.
- El stack `backend-fastapi`, el README, las atribuciones, las pruebas y el inventario reflejan el nuevo catalogo.
- El framework avanzo a `0.2.0-alpha.9` con 18 Skills y 35 archivos inventariados.

**Evidencia:**

- `quick_validate.py` aprobo `seguridad-backend` e `iniciar-proyecto`.
- El contrato de plantilla aprobo.
- Las 44 pruebas automaticas aprobaron.
- Una prueba integral instalo `seguridad-backend` junto con `fastapi-setup` y comprobo todos sus archivos byte por byte.

**Resultado:**

La plantilla dispone de una puerta de seguridad backend verificable sin ampliar el core automatico. El piloto creado con `0.2.0-alpha.8` conserva su estado original y requiere una confirmacion separada para incorporar la nueva Skill.

### 2026-08-28 — Rev 29

**Completado:**

- Se creo `D:\PROYECTOS\piloto-inventario-api` mediante `scripts/crear_proyecto.py`, con el core automatico y la Skill confirmada `fastapi-setup`.
- El piloto configuro FastAPI, pydantic-settings, pytest y httpx con `uv`; el entorno selecciono Python 3.11.15.
- Se implementaron configuracion tipada, `GET /salud`, `GET /productos` y `POST /productos`, con rutas, esquemas y servicio en memoria separados.
- Cinco pruebas aprobaron y un recorrido E2E local comprobo salud, alta de un producto y lectura posterior.
- La memoria generada aprobo `scripts/verificar_memoria_proyecto.py . --json` sin placeholders ni pendientes.

**Friccion observada:**

- La identidad aislada del editor creo archivos que el usuario local no pudo leer durante la sesion. Las pruebas se ejecutaron desde la misma identidad con un cache temporal de uv; es una limitacion del entorno de esta validacion, no una conclusion sobre la plantilla.
- Starlette TestClient emitio una advertencia deprecada con la combinacion instalada de httpx; las pruebas aprobaron, pero debe revisarse antes del cierre del piloto.

**Resultado:**

El primer piloto queda iniciado y valida el uso real del selector y del stack FastAPI hasta su primer modulo. No satisface todavia el criterio de dos pilotos cerrados: falta persistencia SQLite y el cierre documentado de este piloto.

### 2026-08-28 — Rev 28

**Completado:**

- El bloque de compatibilidad Python, coherencia de validaciones y estados Git se registro en `08b0b41`.
- Se exporto ese commit mediante `git archive` hacia una ruta temporal aislada.
- El contrato y las 44 pruebas aprobaron sin utilizar archivos ignorados del arbol activo.
- El ZIP y el directorio de exportacion se eliminaron despues de la comprobacion.
- La rama local `main` se adelanta por fast-forward al cierre documental, sin `push`, rebase ni eliminacion de ramas.

**Resultado:**

La auditoria local previa a pilotos queda cerrada. Los siguientes criterios de salida requieren una decision externa: publicar para ejecutar la matriz remota, iniciar los dos pilotos o completar la procedencia necesaria para redistribucion.

### 2026-08-28 — Rev 27

**Completado:**

- Se reemplazo `Path.write_text(newline=)`, que no forma parte de Python 3.9, por escritura mediante `Path.open` compatible con el piso declarado.
- Se agrego `pruebas/prueba_compatibilidad_python.py` para analizar la gramatica 3.9, impedir APIs de `pathlib` posteriores y comparar constantes deliberadamente duplicadas.
- Se endurecio la deteccion de repositorios Git preexistentes invalidos, con cambios rastreados o preparados y con operaciones merge, rebase, cherry-pick, revert o bisect activas.
- Se probaron repositorios limpios con historial, repositorios sin primer commit, cambios rastreados y operaciones activas, preservando siempre el `.git` preexistente.
- El framework avanzo a `0.2.0-alpha.8`.

**Evidencia:**

- El contrato de plantilla aprobo.
- Las 44 pruebas automaticas aprobaron con Python 3.13.7 en Windows.
- La prueba estatica recorrio todos los modulos Python con la gramatica 3.9.
- No se modificaron Skills durante este bloque.

**Limite:**

El entorno local no dispone de un interprete Python 3.9. La compatibilidad ejecutada realmente en Python 3.9 y en Ubuntu continua pendiente de GitHub Actions; el analisis estatico reduce el riesgo, pero no sustituye esa matriz.

**Resultado:**

La auditoria local de coherencia, compatibilidad declarada y estados Git queda implementada. Falta registrar el cambio y repetir la suite desde una exportacion Git limpia.

### 2026-08-27 — Rev 26

**Completado:**

- Los limites de publicacion, permisos y recursos se registraron en el commit `534e906`.
- Se valido una exportacion limpia del commit y se eliminaron sus temporales.

**Evidencia:**

- El contrato aprobo desde la exportacion limpia.
- Las 38 pruebas automaticas aprobaron desde la exportacion limpia.
- Los escenarios de JSON, valores, archivo grande, permisos, caché y publicacion tardia volvieron a aprobar fuera del arbol activo.

**Resultado:**

Los limites operativos y la limpieza asociada son reproducibles desde Git y no dependen de residuos locales ignorados.

### 2026-08-27 — Rev 25

**Completado:**

- Se retiro un `__pycache__` ignorado que podia filtrarse en copias creadas desde el arbol activo.
- Se rechazan cachés, bytecode, archivos especiales, archivos regulares con `setuid` o `setgid` y arboles desproporcionados.
- Se acotaron archivos, suma total, cantidad de entradas, JSON y valores configurables.
- El creador normaliza permisos del temporal y el inicializador directo exige escritura del propietario en artefactos administrados.
- El destino se vuelve a comprobar inmediatamente antes de publicar.
- Git y el subproceso inicializador tienen tiempos maximos.
- El framework avanzo a `0.2.0-alpha.7`.

**Evidencia:**

- El contrato aprobo.
- Las 38 pruebas automaticas aprobaron.
- Se probaron limites individual, acumulado, cantidad de entradas, JSON y valor configurable.
- Se probaron temporal de solo lectura, copia manual no escribible, caché generada y destino aparecido antes de publicar.

**Resultado:**

La creacion dispone de limites previsibles y no reemplaza un destino observado al final del proceso. Permanece la limitacion inevitable de mejor esfuerzo frente a una carrera hostil entre la comprobacion final y la llamada atomica del sistema.

### 2026-08-27 — Rev 24

**Completado:**

- La proteccion de rutas y enlaces se registro en el commit `6214737`.
- Se valido una exportacion limpia del commit y se eliminaron sus temporales.

**Evidencia:**

- El contrato aprobo desde la exportacion limpia.
- Las 30 pruebas automaticas aprobaron desde la exportacion limpia y sin omisiones.
- Los dos escenarios con enlaces volvieron a ejecutarse correctamente fuera del arbol activo.

**Resultado:**

Las defensas de limites del sistema de archivos son reproducibles desde Git y no dependen del checkout de desarrollo.

### 2026-08-27 — Rev 23

**Completado:**

- El creador valida el arbol fuente antes de descubrir o copiar Skills.
- El inicializador directo valida la copia antes de leer el contrato.
- Se rechazan enlaces simbolicos, junctions, reparse points y cruces de dispositivo internos.
- El destino se comprueba de forma lexica y resuelta; `lexists` detecta enlaces rotos.
- El framework avanzo a `0.2.0-alpha.6`.

**Evidencia:**

- El contrato aprobo.
- Las 30 pruebas automaticas aprobaron sin omisiones.
- Una copia manual con un enlace hacia un archivo externo fallo antes de crear Git, mantuvo todas sus huellas y no altero el objetivo externo.
- Un destino ocupado por un enlace roto fue rechazado sin crear el objetivo ni abandonar temporales.

**Resultado:**

La creacion ya no sigue redirecciones del sistema de archivos presentes en la plantilla o en el nombre final del destino.

### 2026-08-27 — Rev 22

**Completado:**

- El endurecimiento contractual se registro en el commit `dfb20d7`.
- Se valido una exportacion limpia del commit y se eliminaron sus temporales.

**Evidencia:**

- El contrato aprobo desde la exportacion limpia.
- Las 28 pruebas automaticas aprobaron desde la exportacion limpia.
- El arbol de trabajo quedo limpio despues del commit funcional.

**Resultado:**

Las validaciones estrictas de contrato y entradas son reproducibles desde Git y no dependen del arbol activo.

### 2026-08-27 — Rev 21

**Completado:**

- El inicializador y el validador aceptan exclusivamente la version y sintaxis contractual soportadas.
- Se validan claves exactas, origenes permitidos y rutas relativas portables sin duplicados.
- Se rechazan campos derivados aportados por JSON o CLI.
- Se eliminan precedencias silenciosas entre JSON, posicionales y argumentos `--valor`.
- Se normalizan saltos de linea y se rechazan controles Unicode invisibles.
- El framework avanzo a `0.2.0-alpha.5`.

**Evidencia:**

- El contrato aprobo.
- Las 28 pruebas automaticas aprobaron.
- Version contractual futura, version del framework mal formada, clave superior desconocida, rutas invalidas y origen invalido fallaron sin crear Git ni alterar la copia.
- Valores derivados, claves repetidas y texto con control bidireccional fallaron sin publicar un destino.

**Resultado:**

Las entradas ya no dependen de precedencias implicitas y un contrato incompatible no puede ejecutarse como si fuera compatible.

### 2026-08-27 — Rev 20

**Completado:**

- La depuracion agnostica se registro en el commit `91346e6`.
- Se valido una exportacion limpia de ese commit y se eliminaron sus temporales.

**Evidencia:**

- El contrato aprobo desde la exportacion limpia.
- Las 23 pruebas automaticas aprobaron desde la exportacion limpia.
- El arbol de trabajo quedo limpio despues del commit funcional.

**Resultado:**

La correccion de referencias y convenciones es reproducible desde Git y no depende del entorno de trabajo activo.

### 2026-08-27 — Rev 19

**Completado:**

- Se retiraron afirmaciones que atribuian a Antigravity requisitos universales de nombres y rutas.
- Las rutas estables se describen como convenciones interoperables del framework y se exige comprobar su descubrimiento en cada herramienta.
- Se elimino del indice generado la referencia inexistente a `documentacion/analisis/`.
- Se agrego una prueba que enlaza stacks, reglas de lecciones y Skills condicionales con su fuente instalable.
- El framework avanzo a `0.2.0-alpha.4`.

**Evidencia:**

- El contrato aprobo.
- Las 23 pruebas automaticas aprobaron.
- Cada uno de los cinco stacks dispone de `LEEME.md` y de una referencia homonima en `lecciones-aprendidas`.
- Las cuatro Skills citadas nominalmente por el indice existen en el catalogo fuente.

**Resultado:**

La documentacion comun deja de prometer descubrimiento automatico por proveedor y las rutas condicionales relevantes quedan respaldadas por pruebas.

### 2026-08-27 — Rev 18

**Completado:**

- La inicializacion transaccional se registro en el commit `c7e76b3`.
- Se exporto `HEAD` mediante `git archive` hacia una ruta temporal independiente.
- La exportacion se elimino despues de la comprobacion.

**Evidencia:**

- El contrato de plantilla aprobo desde la exportacion limpia.
- Las 22 pruebas automaticas aprobaron desde la exportacion limpia.
- El arbol de trabajo quedo limpio despues del commit funcional.

**Resultado:**

La evidencia confirma que la atomicidad no depende de archivos sin registrar ni de residuos del entorno de desarrollo.

### 2026-08-27 — Rev 17

**Completado:**

- `preparar_cambios` comprueba el contenido resultante y rechaza valores que reintroduzcan placeholders antes de escribir.
- La inicializacion directa se agrupo en una transaccion con respaldo de archivos configurables y del centinela.
- Ante un fallo se eliminan solamente `.env`, estado, directorios y `.git` creados por esa ejecucion, con validacion estricta de la ruta Git.
- Las escrituras temporales y el estado usan reemplazo atomico; los temporales residuales se limpian.
- El framework avanzo a `0.2.0-alpha.3`.
- Se agregaron tres pruebas sobre copias manuales completas.

**Evidencia:**

- El contrato aprobo.
- Las 22 pruebas automaticas aprobaron.
- Un valor `{{VALOR_FUTURO}}` fue rechazado y todas las huellas de la copia permanecieron iguales.
- Una copia con `.gitignore` incapaz de proteger `.env` fallo despues de `git init`, elimino el `.git` nuevo y conservo `.plantilla-framework`.
- Un obstaculo deliberado en `infraestructura/` provoco un fallo posterior a las escrituras y comprobo la restauracion byte por byte, incluida la eliminacion de `.env` y Git creados por el intento.

**Resultado:**

La ruta manual deja de depender exclusivamente de la atomicidad del creador externo. Tanto el flujo recomendado como la contingencia directa evitan publicar o conservar una inicializacion parcial en los fallos cubiertos.

### 2026-08-27 — Rev 16

**Alcance:**

- El usuario indico continuar las correcciones del framework sin crear todavia un proyecto nuevo.

**Completado:**

- Se eliminaron afirmaciones absolutas y obsoletas sobre herramientas, sandbox y descubrimiento automatico en los deltas de Antigravity, Claude y Codex.
- Se retiro la atribucion incorrecta `Antigravity (OpenAI)` y la referencia inexistente `.agents/rules/{{NOMBRE_PROYECTO}}_contexto.md`.
- `plantilla/AGENTS.md` ahora exige comprobar capacidades observables de cada sesion.
- El contrato avanzo a version `2` y el framework a `0.2.0-alpha.2`.
- `NOMBRE_PROYECTO_ENV` se deriva con escape JSON; nombre e idioma rechazan caracteres de control y longitudes no razonables.
- El registro inicial del proyecto ya no copia el historial del framework. Documenta version, Skills instaladas y siguiente paso propios.
- Se creo `pruebas/prueba_compatibilidad_agentes.py` y se ampliaron las pruebas de creacion con entradas dotenv adversariales y memoria inicial.
- Una exportacion limpia de `HEAD` revelo que el inventario dependia de CRLF/LF. `scripts/inventariar_skills.py` ahora canoniza texto UTF-8 a LF y el inventario avanzo a version `2`.

**Tecnologias:**

- Python 3, `unicodedata`, `json`, placeholders derivados y `unittest`.

**Evidencia local:**

- El contrato de plantilla aprobo.
- Las 19 pruebas automaticas aprobaron.
- Un nombre con comillas y `#` quedo escapado; un nombre con salto de linea fue rechazado sin publicar el destino.
- El barrido no encontro las afirmaciones obsoletas ni la ruta inexistente corregida.
- Una prueba dedicada demostro que el mismo `SKILL.md` produce la misma huella con LF y CRLF.

**Resultado:**

La plantilla deja de depender de suposiciones sobre productos concretos, evita inyeccion de lineas en dotenv y entrega una memoria inicial perteneciente al proyecto generado. Los pilotos siguen pospuestos por decision del usuario.

**Registro y reproducibilidad:**

- `ac08dab` registra compatibilidad, dotenv y memoria inicial.
- `62d3db3` normaliza el inventario entre plataformas.
- El clon local fue bloqueado por la proteccion de propiedad de Git y no se modifico la configuracion global.
- Una exportacion limpia mediante `git archive HEAD` aprobo el contrato y las 19 pruebas; el archivo y directorio temporales se eliminaron.

### 2026-08-27 — Rev 15

**Decision del usuario:**

- El catalogo fuente conserva las 17 Skills.
- Todo proyecto nuevo instala automaticamente `cerrar-modulo`, `lecciones-aprendidas` y `probar-e2e`.
- Las demas Skills requieren seleccion explicita; el agente puede recomendarlas, pero no instalarlas sin confirmacion nominal.

**Completado:**

- Se creo `scripts/catalogo_skills.py` con descubrimiento tipado, categorias `core`, `opcional` y `stack`, y salida legible o JSON.
- `scripts/crear_proyecto.py` excluye el almacen completo durante la copia base y agrega solo el core automatico mas cada `--skill NOMBRE` validada.
- El creador conserva la operacion atomica, rechaza nombres desconocidos antes de copiar y mantiene byte por byte cada Skill seleccionada.
- `plantilla/scripts/inicializar_proyecto.py` comprueba que la seleccion declarada coincida con los manifiestos instalados y la registra en `.estado-plantilla.json`.
- La Skill `iniciar-proyecto` separa recomendacion y autorizacion, exige confirmacion exacta y documenta la CLI repetible.
- Los `LEEME.md` de los cinco stacks distinguen catalogo fuente e instancia generada y dejaron de recomendar movimientos manuales.
- `inicializar_proyecto.sh` se redujo a un adaptador que delega en Python y elimino la segunda implementacion obsoleta del selector.
- El README y el indice de lectura reflejan que solo existen en cada proyecto las Skills efectivamente instaladas.
- Se agrego `pruebas/prueba_catalogo_skills.py` y se ampliaron las pruebas integrales con seleccion mixta y rechazo seguro.
- Se actualizo el inventario SHA-256 sin eliminar ninguna Skill.

**Tecnologias:**

- Python 3 con `argparse`, `pathlib`, `shutil`, `TypedDict` y biblioteca estandar.
- `unittest` para pruebas deterministas sin dependencias externas.

**Evidencia:**

- Las 17 Skills aprobaron `quick_validate.py` de `skill-creator`.
- `python scripts/validar_contrato_plantilla.py` aprobo.
- Las 14 pruebas automaticas aprobaron.
- Una instancia predeterminada contuvo exactamente tres Skills y una instancia seleccionada contuvo exactamente seis; todas coincidieron byte por byte con la fuente.
- Una Skill desconocida fue rechazada sin destino publicado ni temporal huerfano.

**Resultado:**

El criterio tecnico de seleccionar solo Skills activas queda implementado y probado. La eficacia real y la calidad de las recomendaciones todavia requieren proyectos piloto; la redistribucion continua bloqueada por procedencia y licencia.

**Registro Git:**

- Commit local: `1153a6f` (`feat: selecciona skills por proyecto`).
- `main` local contiene el cambio funcional; no se ejecuto `push` ni se elimino ninguna rama.

### 2026-08-26 — Rev 14

**Autorizacion:**

- El usuario autorizo modificar las Skills cuando la mejora aumente su eficacia, eficiencia o seguridad.
- Se mantiene la prohibicion de eliminar Skills sin confirmacion y de redistribuir contenido con procedencia pendiente.

**Completado:**

- Se aplico la guia oficial `skill-creator` para reducir instrucciones genericas, preservar alcance y ajustar detalle al riesgo.
- `iniciar-proyecto` se reconstruyo como interfaz conversacional del contrato y la CLI Python; se eliminaron el catalogo duplicado, los placeholders antiguos, los movimientos y los borrados recursivos.
- `agentes-multiagent` se redujo de una implementacion extensa e incompleta a criterios de arquitectura, limites de autoridad, aislamiento, observabilidad y evaluacion adversarial.
- `fastapi-setup` ahora exige secretos sin valor predeterminado, valida `uv.lock` y evita afirmaciones promocionales no comprobadas.
- `nextjs-fullstack` declara cache de forma explicita para no depender de valores predeterminados que cambiaron entre versiones.
- `rag-local` y `fine-tuning-llm` eliminan precios, modelos, licencias, VRAM y tamaños de dataset presentados como universales.
- Los placeholders de idioma no procesados se reemplazaron por la regla canonica de `AGENTS.md`.
- La atribucion de `mobile-flutter` ya no afirma MIT como hecho verificado.
- Se agrego `pruebas/prueba_calidad_skills.py` y se regenero el inventario SHA-256.

**Evidencia:**

- Las 17 Skills aprobaron `quick_validate.py` de `skill-creator`.
- El contrato de la plantilla aprobo.
- Ocho pruebas automaticas aprobaron, incluida una creacion completa con copia byte por byte de las Skills modificadas.
- El barrido no encontro borrado recursivo, secretos predeterminados, placeholders contractuales, precios rigidos ni referencias al wizard Bash dentro de `SKILL.md`.

**Resultado:**

La validacion estructural y las invariantes de seguridad quedan aprobadas. Todavia no se declara eficacia funcional: faltan pilotos comparativos por Skill y la auditoria de procedencia continua bloqueando la redistribucion.

### 2026-08-26 — Rev 13

**Completado:**

- Se creo `scripts/inventariar_skills.py` fuera del arbol congelado.
- El script lee 32 archivos y 17 manifiestos `SKILL.md`, y calcula tamaño y SHA-256 sin escribir dentro de `.agents/skills`.
- Se genero `auditoria/inventario_skills.json` con una huella conjunta determinista.
- El detector encontro una sola declaracion explicita de procedencia, ubicada en `stacks/mobile-flutter/LEEME.md`.
- Se creo `pruebas/prueba_inventario_skills.py` para exigir que el inventario registrado coincida byte por byte con una regeneracion en memoria.
- `ATRIBUCIONES.md` y el README enlazan el inventario mecanico y explican su alcance.

**Prueba local:**

- El contrato de plantilla aprobo.
- La suite ejecuto cinco pruebas y todas aprobaron.
- Git no mostro modificaciones bajo `plantilla/.agents/skills/`.

**Resultado:**

Existe una linea base verificable para detectar cualquier cambio futuro en Skills. El inventario no demuestra autoria ni licencia; solo fija el contenido que debe auditarse.

### 2026-08-26 — Rev 12

**Completado:**

- Se reviso el historial consolidado de la rama de estabilizacion.
- Git confirmo que `main` era ancestro directo de `codex/estabilizacion-framework`.
- La diferencia contenia siete commits adicionales y ninguna modificacion bajo `plantilla/.agents/skills/`.
- La rama local `main` se adelanto por fast-forward hasta `17a86c0`.
- Se conservaron `codex/estabilizacion-framework`, `master` y el worktree preexistente; no se elimino ni reescribio ninguna referencia.
- No se ejecuto ningun `push`.

**Resultado:**

La linea principal local contiene la estabilizacion comprobada. `origin/main` permanece sin cambios y la publicacion sigue bloqueada por la auditoria de procedencia y licencia de Skills.

### 2026-08-26 — Rev 11

**Completado:**

- Se registro la suite y la matriz de CI en el commit `864ba88`.
- Se creo un clon local limpio de `codex/estabilizacion-framework` en un directorio temporal.
- El clon apunto exactamente a `864ba88`, mantuvo el arbol limpio y aprobo el validador del contrato.
- Las cuatro pruebas integrales aprobaron desde el clon sin depender de archivos sin versionar del arbol original.
- El clon temporal se elimino despues de completar la verificacion.

**Resultado:**

La reproducibilidad local de la rama queda comprobada. La Fase 7 solo conserva como pendiente la ejecucion real de la matriz en GitHub Actions; esa ejecucion no justifica publicar sin una decision expresa sobre el riesgo de licencia.

### 2026-08-26 — Rev 10

**Completado:**

- Se creo `pruebas/prueba_creacion_proyecto.py` con la biblioteca estandar de Python.
- La suite cubre configuracion completa, validacion de pendientes, limpieza atomica tras fallo y rechazo de sobrescritura.
- La prueba integral confirma que Git se inicializa, `.env` queda ignorado y todas las huellas SHA-256 de Skills permanecen identicas.
- Se creo `.github/workflows/validacion.yml` con una matriz para Ubuntu y Windows en Python 3.9 y 3.12.
- El README documenta los comandos de validacion local y el alcance de la suite.

**Prueba local:**

- `python scripts/validar_contrato_plantilla.py` finalizo correctamente.
- `python -m unittest discover -s pruebas -p "prueba_*.py" -v` ejecuto cuatro pruebas y todas aprobaron.
- `git diff --check` no detecto errores de whitespace.
- El estado de Git no mostro cambios bajo `plantilla/.agents/skills/`.

**Pendiente:**

La matriz de CI no se considera aprobada hasta que GitHub Actions la ejecute en ambas plataformas. No se publicara la rama como parte implicita de esta fase.

### 2026-08-26 — Rev 9

**Completado:**

- Se corrigio el verificador para detectar los marcadores TODO que crea `--permitir-pendientes`.
- Se comprobo que una configuracion completa obtiene resultado valido y que una configuracion parcial obtiene error con las seis claves pendientes y sus rutas.
- Se reescribio el flujo de inicio del README para usar `scripts/crear_proyecto.py` como entrada soportada.
- Se agrego `ejemplos/configuracion_proyecto.ejemplo.json` para evitar comandos extensos y facilitar una configuracion completa.
- El README ahora distingue el creador soportado, la copia manual de contingencia, el respaldo Bash deprecado y el wizard congelado.
- Se corrigieron el inventario contradictorio de FastAPI, la estructura documental y las afirmaciones no verificadas sobre descubrimiento automatico por agente.

**Prueba aislada:**

- Se ejecuto literalmente el flujo documentado con la configuracion de ejemplo.
- El proyecto resultante configuro 14 archivos, paso la verificacion de memoria, inicializo Git y mantuvo `.env` ignorado.
- El destino temporal se elimino despues de completar las comprobaciones.

**Resultado:**

La Fase 5 queda completada para todo el alcance externo a Skills. La Skill `iniciar-proyecto` permanece congelada, no se modifica y no forma parte del flujo soportado. La Fase 6 queda en espera por la misma restriccion y el trabajo avanza a pruebas automaticas y CI.

### 2026-08-26 — Rev 8

**Completado:**

- Se agregaron `PLAN_DESARROLLO.md`, `DOCUMENTACION_TECNICA.md` y `GUIA_OPERACION.md` a la plantilla.
- Los tres documentos se incorporaron al contrato canonico de placeholders.
- Se creo `plantilla/scripts/verificar_memoria_proyecto.py` con salida legible y JSON para comprobar los siete documentos obligatorios.
- El verificador rechaza archivos ausentes, archivos vacios y placeholders configurables pendientes.
- Se comprobo que el contrato sigue siendo valido y que el script posee sintaxis Python valida.

**Prueba aislada:**

- Se genero `Proyecto Documentado` en un directorio temporal mediante la CLI soportada.
- Se configuraron 14 archivos y no quedaron datos pendientes.
- Los siete documentos de memoria existieron, contuvieron texto y no conservaron placeholders configurables.
- Las huellas SHA-256 de los 32 archivos bajo `.agents/skills` coincidieron antes y despues de generar el proyecto.
- El directorio temporal se elimino despues de completar las verificaciones.

**Resultado:**

Las referencias documentales obligatorias ya existen y pueden comprobarse de forma automatizada. La Fase 5 continua con la correccion del README; el wizard permanece congelado y fuera del alcance de estos cambios.

### 2026-08-26 — Rev 7

**Completado:**

- Se creo `scripts/crear_proyecto.py` como comando de entrada desde el meta-repositorio.
- El creador rechaza destinos existentes y destinos ubicados dentro del propio framework.
- La copia se prepara en un directorio temporal hermano y solo se renombra al destino final cuando el inicializador termina correctamente.
- Un fallo elimina exclusivamente el temporal validado y no deja un proyecto parcial.

**Prueba aislada:**

- Se creo `Proyecto Comercial` mediante un solo comando hacia un destino temporal inexistente.
- Se verifico la creacion del proyecto y el rechazo de un segundo intento sobre el mismo destino.
- No quedaron directorios temporales huerfanos.
- Las huellas SHA-256 de todas las Skills coincidieron entre `plantilla/` y el proyecto generado.
- El proyecto temporal se elimino despues de la prueba.

**Resultado:**

La Fase 4 queda completada. El wizard `iniciar-proyecto` no se actualiza porque pertenece al conjunto de Skills congeladas; la CLI Python constituye mientras tanto la ruta comprobada y soportada.

### 2026-08-26 — Rev 6

**Completado:**

- Se reconstruyo `plantilla/scripts/inicializar_proyecto.py` para consumir `configuracion_plantilla.json`.
- El inicializador procesa exclusivamente los archivos declarados y no recorre `.agents/skills`.
- Se agrego soporte para configuracion JSON, valores `CLAVE=VALOR`, valores predeterminados y pendientes explicitos.
- Se agregaron validaciones de claves desconocidas, datos obligatorios, nombres portables, estado Git y proteccion de `.env`.
- Se separo el nombre visible del identificador tecnico mediante `IDENTIFICADOR_PROYECTO`.
- La escritura de archivos configurables usa respaldo temporal y restauracion ante errores de E/S.
- Se conserva la procedencia en `.estado-plantilla.json` y se rechaza una segunda inicializacion accidental.
- Los cargadores JSON rechazan claves duplicadas.

**Prueba aislada:**

- Se copio `plantilla/` a un directorio temporal.
- Se inicializo `Proyecto Ágil 2` con pendientes permitidos.
- Se configuraron 11 archivos y se marcaron 6 datos pendientes.
- `.env` quedo ignorado y utilizo `proyecto_agil_2` como identificador tecnico.
- El nombre visible con acento se conservo en `PROJECT_NAME`.
- Una segunda ejecucion fue rechazada.
- Las huellas SHA-256 de todos los archivos bajo `.agents/skills` fueron identicas antes y despues.
- El directorio temporal se elimino despues de verificar el resultado.

**Pendiente de la Fase 4:**

- Crear un comando desde la raiz del meta-repositorio que copie `plantilla/` hacia un destino y ejecute este inicializador interno.
- Agregar pruebas automatizadas permanentes para los casos verificados manualmente.

### 2026-08-26 — Rev 5

**Completado:**

- Se creo `plantilla/configuracion_plantilla.json` como fuente unica de placeholders configurables.
- El contrato excluye expresamente `.agents/skills` mientras las Skills permanecen congeladas.
- Se creo `scripts/validar_contrato_plantilla.py` con tipado explicito y validacion estructural.
- Se unifico el vocabulario de `plantilla/AGENTS.md` y `SYSTEM_PROMPT_BASE.md` con `PROJECT_STATE.md`.
- Se eliminaron de los archivos configurables los alias `DESCRIPCION_PRODUCTO_UNA_LINEA`, `OBJETIVO_INMEDIATO`, `DESCRIPCION_PRODUCTO_COMPLETA`, `LISTA_PRIORIDADES_NUMERADA`, `LISTA_PRIORIDADES`, `EXCLUSIONES_MVP`, `SECCION_ARQUITECTURA` y `PROYECTO`.
- El comando `python scripts/validar_contrato_plantilla.py` finalizo correctamente.
- Se confirmo que esta fase no modifica ninguna Skill.

**Limite deliberado:**

Los placeholders operativos que viven dentro de Skills no forman parte del contrato de inicializacion mientras su procedencia se encuentre en revision. El validador no los modifica ni los interpreta como configuracion del proyecto.

**Resultado:**

La Fase 3 queda completada. La Fase 4 puede reconstruir el inicializador para consumir el manifiesto sin duplicar nombres ni reglas de sustitucion.

### 2026-08-26 — Rev 4

**Completado:**

- Se agregaron `.gitignore` y `.gitattributes` en la raiz del meta-repositorio.
- Se agregaron `.gitignore` y `.gitattributes` en `plantilla/` para que cada proyecto generado herede las protecciones.
- Se verifico con `git check-ignore` que `.env` queda ignorado y `.env.ejemplo` permanece permitido en ambos niveles.
- Se verifico con `git check-attr` que Markdown, Python y Bash usan finales de linea LF.
- Se creo `ATRIBUCIONES.md` con la procedencia conocida, los vacios de trazabilidad y la politica temporal de congelacion.
- Se comprobo que el diff de esta revision no modifica ninguna ruta bajo `plantilla/.agents/skills/`.

**Pendiente de la Fase 2:**

- Identificar las fuentes, revisiones y licencias exactas de cada Skill adaptada.
- Decidir si cada contenido externo se conserva con su aviso, se reemplaza, se excluye o requiere permiso.
- Agregar una licencia raiz solo cuando su alcance pueda definirse sin cubrir material de derechos inciertos.

**Decision:**

La proteccion tecnica puede cerrarse y versionarse, pero la licencia global queda diferida. Este pendiente no bloquea las correcciones del inicializador y la documentacion que no modifican Skills.

### 2026-08-26 — Rev 3

**Completado:**

- Se creo el commit `1274132` (`docs: establece memoria y linea base del framework`).
- Se confirmo que `origin/main` es ancestro directo de la rama de estabilizacion y que la integracion futura admite fast-forward.
- Se creo la rama local `main` en `1274132` y se configuro para rastrear `origin/main`.
- Se conservo `master` en `4f958a6` hasta que la publicacion remota se complete y se confirme que ya no se necesita.
- Se creo un clon local temporal de `main` y se verifico que su `HEAD` fuera `1274132`, que su arbol estuviera limpio y que contuviera los archivos requeridos.
- El clon temporal se elimino despues de completar la verificacion.

**Resultado:**

La Fase 1 queda completada localmente. `main` contiene una linea base limpia, lineal y reproducible. La publicacion en `origin/main` se difiere hasta cerrar los riesgos criticos de seguridad y licencia de la Fase 2.

**Riesgo detectado al iniciar la Fase 2:**

El repositorio publico atribuido como fuente del stack `mobile-flutter` no mostro un archivo de licencia en el arbol revisado el 2026-08-26. La declaracion local de licencia MIT no se considera verificada hasta encontrar evidencia primaria o recibir permiso del autor.

El usuario indico que otras Skills tambien pueden contener adaptaciones de productos comerciales o repositorios publicos. Todo `plantilla/.agents/skills/` queda congelado: no se modifica, agrega ni elimina contenido durante las correcciones actuales.

### 2026-08-26 — Rev 2

**Completado:**

- Se elimino `_dryrun2/` con autorizacion explicita del usuario.
- Se revisaron los grupos pendientes con `git diff --check` y una busqueda de formatos comunes de secretos.
- Se creo el commit `1aeed87` (`feat: consolida core y stacks consumibles`).
- Se creo el commit `f845050` (`feat: registra inicializador alfa en Python`).
- El inicializador Python supero una validacion sintactica mediante `ast.parse`.
- El inicializador Bash no pudo validarse porque el subsistema Bash/WSL devolvio acceso denegado antes de analizar el archivo.

**Decisiones:**

- Los defectos conocidos del inicializador alfa se corregiran sobre una linea base versionada para mantener trazabilidad.
- La imposibilidad de iniciar Bash en el entorno actual se registra como validacion pendiente, no como fallo del script.

**Pendiente:**

- Registrar la documentacion del meta-repositorio y los archivos de estado.
- Confirmar que el arbol quede limpio despues de consolidar la linea base.
- Definir la integracion posterior de la rama de estabilizacion en `main`.

### 2026-08-26 — Rev 1

**Completado:**

- Se reviso el estado real de Git sin modificar archivos preexistentes.
- Se confirmo la divergencia entre `master` local y `origin/main`.
- Se creo la rama segura `codex/estabilizacion-framework`.
- Se creo este registro persistente de correcciones.
- Se actualizo `PROJECT_STATE.md` para reflejar el inicio del endurecimiento.
- Se clasifico el arbol pendiente en meta-repositorio, core consumible, stacks, inicializacion y evidencia temporal.
- Se determino que `_dryrun2/` no debia versionarse y se elimino con autorizacion explicita del usuario.
- Se comprobo que los cambios pendientes no contienen errores de whitespace detectables por `git diff --check`.
- Se ejecuto una busqueda de formatos comunes de secretos y no se encontraron credenciales con esos patrones.

**Evidencia:**

- Rama de trabajo: `codex/estabilizacion-framework`.
- Base preservada: commit `4f958a6`.
- Referencia remota observada: `origin/main` en `831e1a6`.

**Pendiente:**

- Definir la secuencia de commits de la linea base.
- Dejar el arbol versionado y reproducible antes de modificar el inicializador.

## 8. Siguiente paso exacto

Comprobar la conclusion de GitHub Actions para `codex/estabilizacion-framework` tras la correccion del inventario; cualquier exposicion futura requiere requisitos de identidad y autorizacion. Mantener bloqueada la redistribucion hasta resolver la procedencia de Skills.

## 9. Bloqueos

La Fase 6 y el cierre legal de la Fase 2 dependen de la futura auditoria de procedencia autorizada por el usuario. Esta restriccion no bloquea las pruebas automaticas ni la CI fuera de Skills.
