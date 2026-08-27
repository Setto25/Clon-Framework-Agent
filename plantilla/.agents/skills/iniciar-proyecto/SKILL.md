---
name: iniciar-proyecto
description: Inicializa una instancia nueva de agent-framework mediante la CLI Python y su contrato canonico. Usar al crear un proyecto desde la plantilla o completar su configuracion inicial. No usar para reorganizar, mover ni eliminar Skills.
---

# Iniciar proyecto

Esta Skill actua como interfaz conversacional de los scripts soportados. No duplica placeholders, no edita el contrato y no selecciona Skills mediante movimientos de carpetas.

## Identificar el contexto

Antes de actuar, comprobar una sola de estas situaciones:

1. **Meta-repositorio:** existen `plantilla/` y `scripts/crear_proyecto.py`. Se crea un destino nuevo fuera de `agent-framework`.
2. **Copia sin inicializar:** existen `.plantilla-framework`, `configuracion_plantilla.json` y `scripts/inicializar_proyecto.py`. Se inicializa esa copia una sola vez.
3. **Proyecto inicializado:** existe `.estado-plantilla.json`. No se vuelve a ejecutar el inicializador; se informa que el proyecto ya fue configurado.

Si las rutas no corresponden a ninguno de esos contextos, detenerse y pedir la ruta correcta.

## Recopilar datos

Leer `configuracion_plantilla.json` como fuente unica de claves. No mantener una lista paralela en esta Skill.

Solicitar solamente los valores obligatorios que falten. Se pueden agrupar en una sola pregunta:

- nombre visible e idioma;
- zona horaria;
- objetivo del producto;
- alcance obligatorio y excluido;
- siguiente paso;
- reglas de arquitectura.

Los valores opcionales pueden conservar sus predeterminados. No se inventan datos del producto.

## Confirmar antes de escribir

Mostrar al usuario:

- contexto detectado;
- destino exacto, cuando corresponda;
- nombre visible;
- claves que se completaran;
- claves que quedarian pendientes;
- si se creara `.env`.

La confirmacion autoriza solamente la creacion o configuracion descrita. No autoriza borrar, mover o publicar contenido.

## Ejecutar la ruta soportada

### Desde el meta-repositorio

Preparar un JSON temporal o usar `--valor CLAVE=VALOR`, y ejecutar:

```powershell
python scripts\crear_proyecto.py <DESTINO_NUEVO> "<NOMBRE_VISIBLE>" --configuracion <CONFIGURACION_JSON>
```

El destino no debe existir ni quedar dentro de `agent-framework`.

### Desde una copia sin inicializar

Ejecutar desde la raiz de la copia:

```powershell
python scripts\inicializar_proyecto.py "<NOMBRE_VISIBLE>" "<IDIOMA>" --configuracion <CONFIGURACION_JSON>
```

No usar el respaldo Bash mientras permanezca deprecado.

### Configuracion incompleta

`--permitir-pendientes` solo se usa cuando el usuario acepta una instancia provisional. Los marcadores generados deben completarse antes de considerar lista la memoria del proyecto.

## Verificar

Ejecutar en la instancia resultante:

```powershell
python scripts\verificar_memoria_proyecto.py .
```

La inicializacion se considera correcta cuando:

- el comando termina con codigo cero;
- no quedan placeholders ni TODO de inicializacion;
- `.env` esta ignorado por Git;
- `.estado-plantilla.json` registra la version de origen;
- Git muestra solamente los archivos esperados de la nueva instancia.

## Skills y stacks

La inicializacion conserva `.agents/skills/` byte por byte. No se activan Skills moviendolas ni se eliminan stacks.

Si el usuario solicita curar el catalogo despues de crear el proyecto, tratarlo como una tarea separada: inventariar, evaluar compatibilidad y pedir autorizacion antes de cualquier cambio. Nunca usar rutas con placeholders en comandos destructivos.

## Entrega

Informar:

- destino creado o copia configurada;
- archivos configurados;
- resultado del verificador;
- existencia y proteccion de `.env`;
- pendientes reales, si el usuario los permitio;
- siguiente paso indicado por `PROJECT_STATE.md`.
