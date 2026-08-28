---
name: iniciar-proyecto
description: Guia una entrevista para crear un proyecto con agent-framework, recomienda Skills y ejecuta la CLI solo despues de confirmar el destino y la seleccion. Usar cuando una persona diga que quiere usar el framework desde su IDE.
---

# Iniciar proyecto

Esta Skill es la entrada conversacional de los scripts soportados. Permite que una persona abra su IDE y diga que quiere usar `agent-framework`, sin conocer JSON ni comandos. La recomendacion de una Skill no autoriza su instalacion.

## Entrada conversacional desde el IDE

Cuando la persona diga "usa el framework", "inicia un proyecto con agent-framework" o una peticion equivalente, se confirma la ruta del meta-repositorio y se leen su `AGENTS.md` y `PROJECT_STATE.md`. Si el IDE ya abrio el meta-repositorio, se usa esa raiz; si no, se solicita o utiliza la ruta que la persona indique.

Se conduce una entrevista breve. Se solicitan en un solo bloque solo los datos que falten:

1. objetivo y usuarios;
2. MVP obligatorio;
3. exclusiones explicitas;
4. infraestructura, stack y restricciones de entorno confirmados;
5. nombre visible y carpeta de destino inexistente;
6. siguiente paso que la persona espera despues de crear la base.

No se obliga a la persona a nombrar Skills ni a editar JSON. El agente convierte las respuestas al contrato de configuracion despues de leer `configuracion_plantilla.json`. Si falta un dato obligatorio, se pregunta; no se inventa ni se interpreta una exclusion como autorizacion para instalar una Skill.

Despues de la entrevista se consulta el catalogo, se recomiendan las Skills adicionales con una razon concreta y se muestra un resumen. Solo al recibir confirmacion explicita del destino y de los nombres exactos se prepara la configuracion y se ejecuta la CLI. Si la persona no confirma, se conserva la conversacion como propuesta y no se escribe nada.

El mensaje minimo que puede usar la persona es:

```text
Usa el framework ubicado en D:\PROYECTOS\agent-framework para iniciar un proyecto nuevo. Guiame con las preguntas necesarias.
```

## Identificar el contexto

Se comprueba una sola de estas situaciones:

1. **Meta-repositorio:** existen `plantilla/`, `scripts/crear_proyecto.py` y `scripts/catalogo_skills.py`. Se crea un destino nuevo fuera de `agent-framework`.
2. **Copia sin inicializar:** existen `.plantilla-framework`, `configuracion_plantilla.json` y `scripts/inicializar_proyecto.py`. Se inicializa esa copia una sola vez. Esta ruta conserva las Skills que ya contenga y no realiza seleccion.
3. **Proyecto inicializado:** existe `.estado-plantilla.json`. No se vuelve a ejecutar el inicializador; una Skill adicional confirmada se incorpora mediante `scripts/agregar_skills.py` desde el meta-repositorio.

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

Cuando el proyecto incluya un backend HTTP o API que se expondra a red, autenticara identidades, aislara recursos por usuario o procesara datos sensibles, se recomienda `seguridad-backend` junto con la Skill del stack correspondiente. Su recomendacion tampoco autoriza instalarla.

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

### Desde un proyecto inicializado

Se confirma cada nombre exacto y se ejecuta desde el meta-repositorio:

```powershell
python scripts\agregar_skills.py <RUTA_PROYECTO> --skill seguridad-backend
```

El comando valida que la instancia y su estado coincidan, prepara las Skills en un temporal, conserva las ya instaladas y actualiza `.estado-plantilla.json` de forma atomica. No reinicializa el proyecto ni reemplaza una Skill existente.

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
