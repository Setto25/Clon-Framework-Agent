# Seguridad y autenticacion

## Separar responsabilidades

- **Autenticacion:** demuestra quien realiza la solicitud.
- **Autorizacion:** decide si esa identidad puede ejecutar la capacidad sobre ese recurso.
- **Aprobacion:** confirma una accion sensible concreta antes de ejecutarla.

El servidor aplica las tres fuera del modelo. Un token valido no concede acceso universal y una descripcion MCP no constituye una politica de autorizacion.

## Perfiles reemplazables

| Escenario | Perfil inicial | Condicion de evolucion |
|---|---|---|
| Prueba privada de un solo usuario | Bearer aleatorio, rotatorio y de alcance minimo | Cambiar cuando existan usuarios, terceros o permisos distintos |
| Usuarios identificados | Proveedor de identidad con tokens verificables | Validar emisor, audiencia, vencimiento y scopes |
| Clientes MCP de terceros | Flujo OAuth compatible con la especificacion vigente | Probar descubrimiento, consentimiento, renovacion y revocacion |
| Servicio a servicio | Identidad de carga o credencial de corta duracion | Evitar secretos estaticos compartidos |

Encapsular la autenticacion tras una interfaz propia que entregue una identidad normalizada. La politica de autorizacion consume esa identidad y el recurso solicitado; no debe depender del formato del proveedor.

## Controles HTTP

- Exponer solo HTTPS en entornos remotos.
- Validar `Host`, origen y redireccionamientos segun el SDK y la topologia real.
- Limitar cuerpo, concurrencia, duracion y frecuencia.
- Aplicar timeouts y listas permitidas a solicitudes salientes.
- Proteger contra SSRF cuando una tool acepta URLs o destinos indirectos.
- No reenviar encabezados de identidad a destinos no confiables.
- Responder con errores que no revelen existencia de recursos cuando la politica lo prohiba.

La proteccion de DNS rebinding o hosts permitidos debe configurarse para el dominio real de produccion; un valor seguro para localhost puede bloquear el despliegue y un comodin puede eliminar la proteccion.

## Secretos y registros

Inyectar secretos mediante el entorno o un gestor de secretos. No incluirlos en imagenes, repositorio, argumentos visibles, respuestas MCP ni trazas. Registrar identidad seudonimizada, capacidad, resultado de autorizacion, duracion y correlacion; omitir tokens, contenidos completos y datos personales innecesarios.

## Contenido no confiable

Tratar argumentos del cliente, resultados de APIs, resources y texto recuperado como datos. Validar estructura y tamaño antes de procesarlos. Si una tool devuelve instrucciones embebidas, el agente consumidor decide bajo sus propias reglas; el servidor no debe elevarlas ni convertirlas en autoridad.

## Pruebas obligatorias

Probar credencial ausente, invalida, vencida y revocada; identidad valida sin permiso; acceso entre usuarios; scopes insuficientes; repeticion de una operacion; entrada sobredimensionada; destino saliente bloqueado; secreto ausente al arrancar y ausencia de secretos en logs y errores.
