# Controles especificos para FastAPI

Se lee esta referencia solo cuando el backend usa FastAPI.

## Limites de responsabilidad

FastAPI ofrece primitivas de autenticacion y autorizacion, pero no decide la politica de negocio. Un `Depends` que valida un token no reemplaza la comprobacion de rol, tenant, propiedad del objeto o campos autorizados.

La terminacion TLS, limites de cuerpo, rate limiting y algunos headers suelen pertenecer al proxy o plataforma. Se identifica el componente responsable y se prueba la configuracion efectiva antes de declararlos cubiertos.

## Configuracion

- `pydantic-settings` carga secretos obligatorios sin valores utilizables por defecto.
- La aplicacion falla de forma controlada si falta una configuracion necesaria.
- CORS enumera origenes confirmados y no combina credenciales con origenes comodin.
- `TrustedHostMiddleware` se considera cuando la aplicacion recibe trafico directo o el proxy preserva el host.
- OpenAPI, `/docs` y `/redoc` se habilitan segun el ambiente y la politica de exposicion.
- Los handlers de excepcion devuelven mensajes externos controlados y conservan detalle solo en observabilidad protegida.

## Contratos y autorizacion

- Cada operacion usa modelos de entrada y salida distintos cuando sus campos autorizados difieren.
- Los modelos no aceptan silenciosamente campos sensibles que el cliente no debe modificar.
- Las dependencias de seguridad resuelven una identidad verificada; la capa de aplicacion comprueba la accion y el recurso concretos.
- Las consultas filtran por identidad o tenant en el servidor y no confian en un identificador del cuerpo.
- Los endpoints administrativos disponen de pruebas con un rol permitido y otro denegado.

## Tokens y contraseñas

- Se elige OAuth2, OpenID Connect, sesiones u otro mecanismo a partir de actores y despliegue confirmados.
- JWT se valida con algoritmos permitidos, emisor, audiencia y expiracion cuando corresponda; su contenido firmado no se trata como cifrado.
- Las claves se rotan y almacenan fuera del codigo segun el proveedor confirmado.
- Las contraseñas usan una biblioteca mantenida y hashing adaptativo; la aplicacion nunca registra la credencial recibida.

## Pruebas FastAPI

- Se reemplazan dependencias mediante `dependency_overrides` para representar al menos dos identidades y roles diferentes.
- Se prueba una misma ruta y un mismo identificador con propietario y no propietario.
- Se inspecciona el JSON de salida para comprobar ausencia de campos internos.
- Se prueban cuerpos demasiado grandes o campos inesperados en el componente que realmente impone el limite.
- La configuracion de produccion se valida sin usar secretos reales en la suite.

## Fuentes consultadas

La redaccion es original y usa documentacion oficial consultada el 2026-08-28:

- Seguridad en FastAPI: https://fastapi.tiangolo.com/tutorial/security/
- OAuth2, JWT y hashing de contraseñas: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- CORS en FastAPI: https://fastapi.tiangolo.com/tutorial/cors/

Se comprueba la version instalada de FastAPI antes de trasladar ejemplos o APIs de la documentacion actual.
