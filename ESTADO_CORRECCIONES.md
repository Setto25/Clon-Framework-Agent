# Estado de correcciones de agent-framework

**Ultima actualizacion:** 2026-08-26 (rev 2)
**Estado general:** Linea base local en consolidacion
**Fase activa:** Fase 1 — estabilizacion Git y linea base
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

## 4. Plan y avance

| Fase | Alcance | Estado | Criterio de salida |
|---|---|---|---|
| 1 | Estabilizar Git y definir la linea base | En curso | Rama canónica definida, arbol limpio y clon reproducible |
| 2 | Seguridad, `.gitignore`, licencia y atribuciones | Pendiente | `.env` protegido, licencia y atribuciones completas |
| 3 | Contrato unico de plantilla y placeholders | Pendiente | Manifiesto valido y placeholders sin duplicidad |
| 4 | Reconstruir el inicializador | Pendiente | Un comando genera un proyecto completo y seguro |
| 5 | Corregir wizard, documentos y referencias | Pendiente | No existen archivos o rutas prometidas ausentes |
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

Registrar la documentacion del meta-repositorio como tercer commit de linea base, verificar que el arbol quede limpio y documentar el mecanismo seguro para integrar posteriormente `codex/estabilizacion-framework` en `main`.

## 9. Bloqueos

No existe un bloqueo tecnico activo.
