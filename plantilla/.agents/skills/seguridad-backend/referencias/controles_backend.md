# Controles para backends HTTP y APIs

Se usa esta referencia para seleccionar controles segun el riesgo observado. No todos aplican a cada sistema.

## Identidad y autorizacion

- Se distingue autenticacion de autorizacion.
- Cada operacion protegida comprueba funcion, objeto y propiedades autorizadas.
- Los identificadores aportados por el cliente nunca demuestran propiedad.
- Los tokens comprueban firma, emisor, audiencia, expiracion y algoritmo permitido cuando esos campos forman parte del protocolo elegido.
- Las contraseñas, si existen, se almacenan con un algoritmo de hashing adaptativo mantenido; nunca se cifran de forma reversible para autenticacion.
- La revocacion, rotacion y duracion de sesiones se definen segun el impacto, no mediante una duracion universal.

## Entrada, salida y datos

- Los esquemas rechazan campos inesperados cuando aceptarlos pueda habilitar asignacion masiva.
- Longitud, rango, cardinalidad, formato y tipo se limitan antes de la logica de negocio.
- La salida usa un contrato dedicado y omite secretos, hashes, permisos internos y campos no necesarios.
- Las consultas parametrizadas u ORM separan datos de instrucciones.
- Las transacciones preservan invariantes y revierten cambios parciales ante fallos.
- Los archivos se validan por contenido, tamaño y destino; no se confia solo en nombre o tipo declarado.

## HTTP y configuracion

- TLS se termina en un componente identificado y su responsabilidad queda documentada.
- CORS enumera origenes necesarios; credenciales y comodines no se combinan.
- Hosts, metodos, tipos de contenido, redirecciones y documentacion se limitan por ambiente.
- Los errores usan codigos coherentes y un cuerpo externo controlado.
- Los headers de seguridad y cache se deciden segun clientes, contenido y proxy confirmado.
- Los endpoints administrativos, de depuracion y observabilidad requieren una politica de acceso explicita.

## Abuso y disponibilidad

- Se identifican flujos costosos o sensibles y se limitan por identidad, origen o recurso segun corresponda.
- Cuerpo, carga de archivos, paginacion, concurrencia y tiempo de ejecucion tienen limites verificables.
- Los reintentos usan topes y retroceso; no multiplican una operacion no idempotente.
- Las respuestas grandes y busquedas no permiten extraccion ilimitada de datos.
- Los limites impuestos por proxy o plataforma se prueban, no se presuponen.

## Dependencias y comunicaciones salientes

- URLs aportadas por usuarios no permiten alcanzar redes, metadatos o esquemas no autorizados.
- Webhooks verifican autenticidad y repeticion cuando el proveedor lo soporta.
- Respuestas de terceros se validan como entrada no confiable.
- Timeouts, errores parciales y circuitos de fallo no dejan transacciones inconsistentes.
- El inventario de endpoints, versiones y dependencias se mantiene alineado con el despliegue.

## Logs y auditoria

- Se registran decisiones de acceso y operaciones sensibles con identificadores de correlacion.
- No se registran contraseñas, tokens completos, secretos ni cuerpos sensibles sin una justificacion y proteccion especificas.
- Los eventos distinguen fallo de autenticacion, denegacion de autorizacion y error interno sin revelar esa diferencia cuando facilite enumeracion indebida.
- La retencion, acceso e integridad de logs pertenecen a una politica confirmada.

## Evidencia minima

| Riesgo | Prueba esperada |
|---|---|
| Acceso sin identidad | El endpoint protegido rechaza la solicitud |
| Escalada de funcion | Un rol comun no ejecuta una accion privilegiada |
| Acceso entre identidades | Un usuario no lee ni modifica recursos ajenos |
| Asignacion masiva | Un campo no permitido se rechaza o ignora de forma deliberada |
| Filtracion | Respuestas y logs no contienen secretos ni campos internos |
| Consumo excesivo | El limite configurado produce una respuesta controlada |
| Dependencia hostil | Timeout, respuesta invalida o URL bloqueada no comprometen el proceso |

## Fuentes consultadas

La redaccion es original y sintetiza criterios consultados el 2026-08-28:

- OWASP Application Security Verification Standard 5.0.0: https://github.com/OWASP/ASVS/tree/v5.0.0_release
- OWASP API Security Top 10 2023: https://owasp.org/API-Security/editions/2023/en/0x11-t10/
- OWASP REST Security Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html

OWASP publica ASVS y la documentacion del proyecto API Security bajo CC BY-SA 4.0. Estos enlaces se usan como fuentes de criterio; no se copia su texto normativo.
