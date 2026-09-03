# Pruebas de interoperabilidad

## Capas de prueba

1. **Dominio:** casos de uso puros, errores y autoridad sin MCP ni red.
2. **Adaptador MCP:** descubrimiento e invocacion en memoria con el SDK cuando sea posible.
3. **Transporte:** Streamable HTTP real, encabezados, limites y cancelacion.
4. **Seguridad:** autenticacion, autorizacion, aprobacion y entradas adversariales.
5. **Empaquetado:** arranque de la imagen con configuracion minima y faltante.
6. **Remoto:** endpoint HTTPS desplegado, reinicio, escalamiento y observabilidad.
7. **Clientes:** al menos dos implementaciones o adaptadores independientes.

La prueba en memoria acelera el ciclo, pero no demuestra encabezados, proxy, TLS ni comportamiento remoto. La prueba con un solo inspector tampoco demuestra independencia del agente.

## Matriz de compatibilidad

Registrar por ejecucion:

| Dimension | Evidencia |
|---|---|
| Revision MCP solicitada y negociada | Solicitud y respuesta observables |
| Cliente o SDK y version | Dependencia fijada o salida de version |
| Transporte | Proceso local o Streamable HTTP |
| Capacidades | Descubrimiento e invocacion verificadas |
| Autenticacion | Perfil, identidad y rechazo esperado |
| Estado | Reinicio y cambio de replica cuando corresponda |
| Resultado | Aprobado, incompatible o no probado |

No inferir compatibilidad por compartir proveedor o lenguaje. Cuando un cliente no soporte la revision actual, documentar el adaptador o modo heredado y conservar una regresion.

## Casos minimos

- inicializacion y negociacion compatibles;
- listado de capacidades y esquema esperado;
- invocacion valida y salida estructurada;
- argumento desconocido, tipo incorrecto y cuerpo excesivo;
- capacidad inexistente;
- timeout y cancelacion;
- error de dependencia sin filtracion interna;
- credencial ausente, invalida y sin permiso;
- repeticion de una accion mutable;
- reinicio entre solicitudes independientes;
- flujo con estado compartido, solo si existe;
- dos clientes que obtienen la misma semantica.

## Doble de prueba y servicios reales

Simular APIs externas para cubrir deterministamente errores y limites. Mantener una prueba de humo separada contra cada dependencia real; debe quedar deshabilitada por defecto si consume dinero, modifica datos o necesita credenciales. Nunca fabricar el resultado de una prueba remota ausente.

## Criterio de evidencia

Guardar comandos reproducibles, versiones, configuración no secreta y resultados resumidos. La documentacion de configuracion de un cliente no equivale a una ejecucion. La portabilidad se demuestra cuando el servidor permanece igual y solo cambia el adaptador de ultima milla.
