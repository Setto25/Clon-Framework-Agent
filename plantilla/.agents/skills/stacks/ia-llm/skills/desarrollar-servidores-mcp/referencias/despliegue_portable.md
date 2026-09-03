# Despliegue portable

## Contrato de ejecucion

El artefacto desplegable debe:

- escuchar en la interfaz y puerto entregados por el entorno;
- iniciar sin escribir configuracion dentro de la imagen;
- terminar correctamente ante la señal de apagado;
- separar salud del servicio y protocolo MCP cuando la plataforma lo necesite;
- emitir logs estructurados sin secretos;
- declarar dependencias y version del runtime de forma reproducible.

Un contenedor OCI es el valor predeterminado, no una obligacion del dominio. El servidor debe poder arrancar como aplicacion ASGI o equivalente y recibir transporte, autenticacion, almacenamiento y telemetria mediante configuracion.

## Configuracion reemplazable

Definir variables o un objeto tipado para:

- entorno, host, puerto y URL publica;
- revision MCP admitida y opciones de compatibilidad;
- autenticacion e identidad;
- limites de solicitud, concurrencia y timeout;
- dependencias externas y almacenamiento;
- nivel de logs y exportador de metricas.

Fallar al arrancar si falta una configuracion obligatoria. No usar valores de desarrollo inseguros como fallback de produccion.

## Perfil inicial de Cloud Run

Cloud Run resulta adecuado para una prueba pequeña porque ejecuta contenedores o despliegues desde fuente, asigna HTTPS y puede escalar a cero. Mantener este perfil en la capa operativa:

- servicio, no trabajo por lotes;
- endpoint Streamable HTTP;
- concurrencia y timeout ajustados al caso medido;
- minimo de instancias en cero cuando la latencia de arranque sea aceptable;
- maximo acotado para contener costos y dependencias;
- secretos mediante el servicio administrado correspondiente;
- acceso autenticado salvo decision explicita y revisada.

La creacion de proyecto, vinculacion de facturacion, habilitacion de APIs, asignacion de roles, publicacion y eliminacion de recursos requieren autorizacion explicita. Verificar precios, cuotas y capa gratuita vigentes antes de ejecutar.

## Migracion entre proveedores

Una migracion no deberia tocar tools ni dominio. Solo sustituye:

- manifiesto o comando de despliegue;
- adaptador de identidad e ingreso;
- gestor de secretos;
- almacenamiento o bus compartido;
- telemetria y escalamiento.

Si el cambio exige reescribir contratos MCP, existe acoplamiento indebido. Si usa estado entre intercambios, comprobar balanceo y persistencia compartida antes de aumentar replicas.

## Promocion segura

Probar la imagen localmente, fijar su huella, desplegar primero en un entorno aislado, ejecutar pruebas remotas, revisar logs y costos observables y documentar rollback. No declarar portable un servidor probado solamente en el emulador o cliente de un proveedor.
