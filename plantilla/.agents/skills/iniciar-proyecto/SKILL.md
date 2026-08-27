---
name: iniciar-proyecto
description: Inicializa una instancia nueva de agent-framework, recomienda Skills segun el contexto y aplica solamente el core automatico mas las Skills confirmadas por el usuario. Usar al crear un proyecto desde la plantilla o completar su configuracion inicial.
---

# Iniciar proyecto

Esta Skill actua como interfaz conversacional de los scripts soportados. La recomendacion de una Skill no autoriza su instalacion.

## Identificar el contexto

Se comprueba una sola de estas situaciones:

1. **Meta-repositorio:** existen `plantilla/`, `scripts/crear_proyecto.py` y `scripts/catalogo_skills.py`. Se crea un destino nuevo fuera de `agent-framework`.
2. **Copia sin inicializar:** existen `.plantilla-framework`, `configuracion_plantilla.json` y `scripts/inicializar_proyecto.py`. Se inicializa esa copia una sola vez. Esta ruta conserva las Skills que ya contenga y no realiza seleccion.
3. **Proyecto inicializado:** existe `.estado-plantilla.json`. No se vuelve a ejecutar el inicializador.

Si las rutas no corresponden a esos contextos, se solicita la ruta correcta.

## Recopilar datos

Se lee `configuracion_plantilla.json` como fuente unica de placeholders. Se solicitan solamente los valores obligatorios que falten y no se inventan datos del producto.

## Recomendar Skills

Desde el meta-repositorio se consulta el catalogo vigente:

```powershell
python scripts\catalogo_skills.py --json
```

El agente contrasta el objetivo, las tecnologias confirmadas, el hardware y el tipo de trabajo con las descripciones del catalogo. Luego presenta:

- las tres Skills automaticas: `cerrar-modulo`, `lecciones-aprendidas` y `probar-e2e`;
- cada Skill adicional recomendada, con una razon breve vinculada al proyecto;
- las Skills dudosas o innecesarias, cuando su exclusion evite ruido o autoridad excesiva.

No se recomienda por coincidencia superficial ni se presupone un stack no confirmado. La recomendacion no se agrega al comando hasta que el usuario confirme sus nombres exactos. Una respuesta ambigua requiere una confirmacion mas precisa.

## Confirmar antes de escribir

Se muestra al usuario el destino, el nombre visible, los datos configurables, las Skills automaticas, las Skills adicionales confirmadas, los pendientes y si se creara `.env`.

La confirmacion autoriza solamente esa creacion. No autoriza eliminar Skills de la fuente, publicar el repositorio ni incorporar recomendaciones no confirmadas.

## Ejecutar la ruta soportada

### Desde el meta-repositorio

Se prepara un JSON temporal o se usa `--valor CLAVE=VALOR`. Cada Skill adicional confirmada se expresa con un argumento independiente:

```powershell
python scripts\crear_proyecto.py <DESTINO_NUEVO> "<NOMBRE_VISIBLE>" --configuracion <CONFIGURACION_JSON> --skill fastapi-setup --skill evaluar-agente
```

El destino no debe existir ni quedar dentro de `agent-framework`. El creador copia solo el core automatico y las Skills nombradas mediante `--skill`. Los stacks no seleccionados permanecen exclusivamente en el catalogo fuente.

### Desde una copia sin inicializar

Se ejecuta desde la raiz de la copia:

```powershell
python scripts\inicializar_proyecto.py "<NOMBRE_VISIBLE>" "<IDIOMA>" --configuracion <CONFIGURACION_JSON>
```

Esta ruta no filtra Skills. Para obtener seleccion explicita se vuelve al meta-repositorio y se usa `scripts/crear_proyecto.py`.

### Configuracion incompleta

`--permitir-pendientes` se usa solo cuando el usuario acepta una instancia provisional. Los marcadores generados se completan antes de considerar lista la memoria del proyecto.

## Verificar

Se ejecuta en la instancia resultante:

```powershell
python scripts\verificar_memoria_proyecto.py .
```

La inicializacion se considera correcta cuando:

- el comando termina con codigo cero;
- no quedan placeholders ni TODO de inicializacion;
- `.env` esta ignorado por Git;
- `.estado-plantilla.json` registra la version y las Skills instaladas;
- los manifiestos `SKILL.md` presentes coinciden exactamente con la seleccion autorizada.

## Entrega

Se informa el destino, los archivos configurados, las Skills instaladas, el resultado del verificador, la proteccion de `.env`, los pendientes reales y el siguiente paso indicado por `PROJECT_STATE.md`.
