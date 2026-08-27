# Estado de correcciones de agent-framework

**Ultima actualizacion:** 2026-08-26 (rev 8)
**Estado general:** Memoria operativa verificable
**Fase activa:** Fase 5 — documentos y referencias externas a Skills
**Rama de trabajo:** `codex/estabilizacion-framework`

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
- Las Skills permanecen congeladas por decision del usuario hasta completar su auditoria de procedencia; cualquier defecto se registra sin editar esos archivos.

## 4. Plan y avance

| Fase | Alcance | Estado | Criterio de salida |
|---|---|---|---|
| 1 | Estabilizar Git y definir la linea base | Completada | Rama canónica definida, arbol limpio y clon reproducible |
| 2 | Seguridad, `.gitignore`, licencia y atribuciones | En curso — procedencia | `.env` protegido, licencia y atribuciones completas |
| 3 | Contrato unico de plantilla y placeholders | Completada | Manifiesto valido y placeholders sin duplicidad |
| 4 | Reconstruir el inicializador | Completada | Un comando genera un proyecto completo y seguro |
| 5 | Corregir wizard, documentos y referencias | En curso — wizard congelado | No existen archivos o rutas prometidas ausentes |
| 6 | Validar Skills, stacks y agentes | Pendiente | Solo se descubren Skills activas y las guias estan comprobadas |
| 7 | Incorporar pruebas y CI | Pendiente | Matriz automatica aprobada en plataformas soportadas |
| 8 | Ejecutar pilotos y publicar `v1.0.0` | Pendiente | Dos pilotos exitosos y release reproducible |

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

Corregir el README para presentar la CLI Python como ruta soportada, eliminar inventarios contradictorios y marcar el wizard congelado como no verificado para el flujo actual.

## 9. Bloqueos

No existe un bloqueo tecnico activo.
