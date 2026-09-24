---
name: diagnosticar-tarea
description: Ejecuta un prediagnostico determinista de proyectos o monorepos con pruebas fallidas, herramientas ausentes o cobertura incierta. Usar antes de atribuir una causa o comenzar una depuracion reproducible.
---

# Diagnosticar tarea

## Objetivo

Reducir el razonamiento exploratorio del agente ejecutando un diagnostico determinista con Python antes de que el agente comience. Python resuelve el "que falla y donde"; el agente se concentra en el "como solucionarlo".

## Cuando activar

- Antes de cualquier tarea que involucre pruebas fallidas o errores reproducibles.
- Antes de depuracion cuando hay un stacktrace o un fallo observable.
- No se activa para tareas de diseno, documentacion o creacion desde cero sin contrato previo.

## Flujo

### Paso 1: prediagnostico local

Ejecutar antes de invocar al agente:

```
python scripts/diagnosticar_tarea.py <directorio>
```

El script recorre modulos anidados, usa `contrato_validacion.json` cuando existe y, en su ausencia, infiere conservadoramente pruebas y puertas desde `pyproject.toml`, `package.json`, `alembic.ini` y configuraciones equivalentes. Cada comando se ejecuta sin shell y desde el directorio del modulo. Ejecutarlo solo sobre un directorio confiable y autorizado: las pruebas son codigo ejecutable.

La salida distingue `APROBADO`, `FALLIDO`, `NO_EJECUTADO` y `NO_DISPONIBLE`; registra comando, directorio, codigo, duracion y evidencia. Un codigo de salida distinto de cero del diagnostico no se puede reinterpretar como exito.

### Paso 2: decision de escalado

Segun el resultado del diagnostico:

- **Confianza alta, fallos estructurados:** entregar el diagnostico como contexto inicial. El agente confirma la causa en las rutas candidatas antes de corregir.
- **Confianza media, fallos parcialmente trazados:** entregar el diagnostico con las trazas disponibles. El agente complementa lo que Python no pudo determinar.
- **Confianza baja o sin pruebas ejecutables:** informar `NO_EJECUTADO`; no afirmar que existen cero fallos ni que las pruebas aprobaron.

### Paso 3: contexto del agente

Si el diagnostico tiene confianza alta o media, incluirlo como primer mensaje:

```
DIAGNOSTICO_PREVIO:
{salida del script en formato texto}

Confirma la causa en los archivos candidatos e implementa las correcciones. No repitas el diagnostico salvo contradiccion con su evidencia.
```

### Paso 4: verificacion

El agente debe ejecutar la validacion despues de aplicar las correcciones. Si nuevos fallos aparecen, puede usar el diagnostico como referencia pero debe investigar las diferencias.

## Relacion con otras Skills

- `optimizar-contexto` gestiona el contexto durante la sesion; `diagnosticar-tarea` reduce el contexto necesario antes de empezar.
- `protocolo-debugging` establece el metodo de depuracion del agente; `diagnosticar-tarea` resuelve la fase de aislamiento antes de que el agente intervenga.
- Las tres son complementarias: diagnostico antes, contexto durante, metodo al depurar.

## Limites

- No aplica correcciones automaticas. El diagnostico es informativo, no ejecutivo.
- No sustituye la puerta de cierre. El agente debe comprobar que las correcciones resuelven los fallos y ejecutar `scripts/validar_cierre_tarea.py`.
- No diagnostica problemas sin contrato observable (sin pruebas, sin errores reproducibles).
- No presenta los archivos candidatos como una causa confirmada; solo usa trazas, imports o cambios relacionados y excluye dependencias, caches y artefactos.
