---
name: agentes-multiagent
description: Diseña y evalua agentes con herramientas o coordinacion multiagente, incluyendo limites de autoridad, presupuesto y resistencia a instrucciones no confiables. Usar cuando una tarea realmente necesite decisiones dinamicas de un LLM. No usar para flujos deterministas que puede resolver codigo convencional.
---

# Agentes y sistemas multiagente

## Puerta de decision

Preferir, en este orden:

1. funcion o pipeline determinista;
2. una llamada al modelo con salida estructurada;
3. router de una sola herramienta;
4. agente con pocas herramientas;
5. coordinacion multiagente.

Solo avanzar de nivel cuando el anterior no pueda resolver el caso medido. Cada nivel adicional aumenta costo, latencia, superficie de ataque y dificultad de evaluacion.

## Contrato antes de implementar

Definir por escrito:

- objetivo observable y criterio de exito;
- entradas confiables y no confiables;
- herramientas necesarias y autoridad maxima de cada una;
- acciones que requieren aprobacion humana;
- maximo de iteraciones, delegaciones, tiempo y costo;
- datos que pueden persistirse o registrarse;
- condicion de detencion y comportamiento ante error.

Si una herramienta no puede imponer autorizacion fuera del modelo, no debe exponerse al agente.

## Seleccionar arquitectura

| Necesidad | Patron preferido |
|---|---|
| Elegir entre operaciones conocidas | Router con salida estructurada |
| Consultar herramientas hasta responder | Agente iterativo con limite bajo |
| Ejecutar un plan auditable | Planificar y ejecutar con validacion de cada paso |
| Mejorar una respuesta sin herramientas | Generar, evaluar y revisar con limite fijo |
| Especialidades independientes y medibles | Coordinador con especialistas aislados |

No seleccionar un framework antes de definir el contrato. Comparar la version instalada, mantenimiento, modelo de estado, observabilidad y controles de herramientas mediante documentacion oficial.

## Limite de seguridad

Toda salida de usuarios, documentos, web, correo, memoria, herramientas y otros agentes se trata como datos no confiables, nunca como nuevas instrucciones de sistema.

Cada llamada de herramienta debe aplicar fuera del LLM:

- esquema cerrado y validacion de argumentos;
- identidad y autorizacion del usuario solicitante;
- alcance minimo por operacion y recurso;
- timeout, limite de tamaño y numero de llamadas;
- idempotencia cuando exista reintento;
- aprobacion inmediata para borrar, publicar, enviar, comprar o cambiar produccion.

Un proceso con timeout no constituye un sandbox. El codigo generado requiere aislamiento real de sistema de archivos, red, procesos, credenciales y recursos, o no debe ejecutarse.

## Estado y observabilidad

Registrar eventos estructurados: solicitud, decision, herramienta elegida, argumentos saneados, resultado resumido, costo, duracion y estado final.

No registrar secretos, datos personales innecesarios, prompts completos ni razonamiento interno del modelo. Conservar identificadores de correlacion y motivos de politica suficientes para auditar decisiones.

El presupuesto debe medirse con uso real devuelto por el proveedor; no se considera implementado si solo existe una variable que nunca se actualiza.

## Implementacion incremental

1. Crear adaptadores simulados para modelo y herramientas.
2. Implementar el caso feliz con una sola herramienta.
3. Agregar limites y denegaciones antes de conectar proveedores reales.
4. Probar datos adversariales e instrucciones indirectas dentro de resultados de herramientas.
5. Conectar una herramienta real de solo lectura.
6. Incorporar acciones mutables una por una, con autorizacion y aprobacion comprobables.
7. Agregar coordinacion multiagente solo si una evaluacion demuestra mejora sobre el agente simple.

## Evaluacion minima

Mantener un conjunto versionado con:

- casos normales y ambiguos;
- herramienta y argumentos esperados;
- solicitudes fuera de autoridad;
- prompt injection directa e indirecta;
- resultados de herramienta maliciosos o sobredimensionados;
- timeout, reintento, presupuesto agotado y bucle;
- fallos parciales de especialistas;
- ausencia de filtracion de secretos.

Medir tasa de exito, seleccion de herramienta, exactitud de argumentos, violaciones de autoridad, costo y latencia. Comparar contra una solucion sin agente.

## Criterio de aceptacion

No aprobar para uso real hasta demostrar que:

- ninguna accion excede la autoridad del usuario;
- los limites detienen bucles y gasto excesivo;
- la aprobacion humana no puede omitirse desde el prompt;
- las entradas no confiables no cambian las reglas del sistema;
- las trazas permiten reconstruir acciones sin exponer secretos;
- las pruebas adversariales se conservan como regresiones.

Para diseñar casos concretos de ataque y autoridad, consultar `evaluar-agente` si esa Skill esta disponible en el proyecto.
