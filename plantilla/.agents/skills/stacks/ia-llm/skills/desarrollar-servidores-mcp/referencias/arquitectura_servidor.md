# Arquitectura de un servidor MCP

## Frontera estable

La logica de negocio no debe conocer JSON-RPC, encabezados HTTP, objetos del SDK ni detalles del proveedor cloud. Una separacion util contiene:

1. **Dominio:** casos de uso, tipos y reglas puras.
2. **Aplicacion:** orquestacion, puertos de almacenamiento y politicas de autoridad.
3. **Adaptador MCP:** convierte tools, resources y prompts en llamadas de aplicacion.
4. **Transporte:** proceso local o Streamable HTTP.
5. **Operacion:** configuracion, identidad, observabilidad, contenedor y plataforma.

Esta frontera permite probar el dominio sin red, cambiar el SDK y desplegar el mismo comportamiento en otra plataforma.

## Eleccion de primitivas

| Necesidad | Primitiva |
|---|---|
| Ejecutar una operacion con argumentos y resultado | Tool |
| Exponer contenido identificable y consultable | Resource |
| Ofrecer una plantilla de interaccion controlada por el usuario | Prompt |

No modelar cada lectura como tool si representa contenido direccionable. No usar prompts para imponer controles de seguridad.

## Transporte y version

Para un servicio remoto nuevo, preferir Streamable HTTP. Mantener el arranque del servidor desacoplado para habilitar un transporte de proceso local cuando una prueba o cliente lo requiera.

La revision MCP 2026-07-28 introdujo un nucleo sin estado y negociacion por solicitud. El servidor debe responder segun la version negociada y probar las revisiones que declare compatibles. Si se admite un cliente anterior, registrar ese modo como compatibilidad deliberada: algunas revisiones y SDK anteriores conservaron sesiones o exigieron afinidad entre replicas.

## Estado y escalamiento

Clasificar cada dato antes de persistirlo:

- **por solicitud:** permanece en memoria y se descarta al responder;
- **efimero compartido:** usa un almacen con expiracion si varias replicas deben continuar un flujo;
- **durable:** pertenece a una base de datos o sistema externo con contrato propio;
- **secreto:** usa un gestor de secretos o inyeccion segura, nunca estado de sesion MCP.

Preferir solicitudes independientes. Si una capacidad necesita multiples intercambios, suscripciones o reanudacion, documentar la clave de correlacion, expiracion, consistencia y comportamiento cuando otra replica recibe el siguiente mensaje. No prometer escalamiento horizontal mientras ese estado permanezca solo en memoria.

## Compatibilidad evolutiva

- Agregar campos opcionales antes de cambiar campos requeridos.
- No reutilizar un nombre publicado con semantica distinta.
- Versionar los contratos del dominio cuando una evolucion incompatible sea inevitable.
- Tratar capacidades negociadas como datos observados, no como atributos inferidos por la marca del cliente.
- Mantener adaptadores de cliente fuera del servidor canonico.

## Resultado esperado

La arquitectura queda aceptable cuando el mismo caso de uso se ejecuta desde una prueba directa del dominio, una prueba MCP en memoria y un endpoint HTTP sin duplicar reglas de negocio.
