# Sintesis de pilotos locales

**Fecha:** 2026-08-28  
**Alcance:** validacion local de `backend-fastapi`, `nextjs-fullstack`, `typescript-react` y `desarrollar-servidores-mcp`.
**Limite:** no constituye una autorizacion de publicacion, despliegue ni redistribucion.

## Resultado

Dos proyectos privados y un fixture reproducible completaron recorridos locales. El selector de Skills instalo solo las capacidades confirmadas, y las pruebas verificaron integracion HTTP real sin crear recursos cloud.

| Piloto | Skills evaluadas | Evidencia local | Estado |
|---|---|---|---|
| `piloto-inventario-api` | `fastapi-setup`, `seguridad-backend` | 7 pruebas, migracion Alembic `20260828_01`, PostgreSQL 18 y recorrido HTTP | Cerrado localmente |
| `piloto-inventario-web` | `nextjs-fullstack`, `typescript-react` | 2 pruebas Vitest, lint, build y recorrido repetido contra FastAPI | Cerrado localmente |
| `pruebas/fixtures/servidor-mcp` | `desarrollar-servidores-mcp` | 12 pruebas, incluidos timeout y salida acotada; cliente Python MCP 2026-07-28, Inspector 2.5.0 con MCP 2025-11-25 y Streamable HTTP autenticado | Hito local aprobado; contenedor y nube pendientes |

## Hallazgos favorables

- El creador genero instancias con el core automatico y con las Skills expresamente autorizadas, sin copiar el catalogo completo.
- La memoria inicial, las guias operativas y el verificador documental hicieron posible reconstruir los comandos de ambos pilotos.
- La separacion entre pruebas aisladas y recorridos sobre servicios reales funciono: SQLite se uso para aislar pruebas del API y PostgreSQL para validar la persistencia local; Next.js consulto el API real por HTTP.
- La puerta `seguridad-backend` mantuvo el alcance correcto: endurecio las entradas y documento limites, sin afirmar cobertura de autenticacion, autorizacion o exposicion que el MVP no requeria.
- El piloto MCP mantuvo el dominio sin imports del SDK ni HTTP, y trato bearer, almacenamiento en memoria, ASGI y plataforma como adaptadores sustituibles.
- La Tool mutable conservo idempotencia ante reintentos y la autorizacion de solo lectura impidio el efecto antes de alcanzar el almacenamiento.

## Fricciones observadas

| Prioridad | Friccion | Efecto | Recomendacion |
|---|---|---|---|
| Alta | Los valores multilinea enviados con `--valor` desde PowerShell conservaron literalmente `` `n`` en la memoria del segundo piloto. | La instancia quedo funcional, pero su estado contiene texto degradado. | Corregida localmente: el inicializador rechaza esa secuencia y dirige a `--configuracion` JSON; una regresion la cubre. |
| Alta | La CI actual valida el framework Python, no los comandos de un frontend generado dentro de `interfaz/`. | El build y las pruebas de Next.js solo tienen evidencia local. | Corregida localmente: `scripts/validar_frontend_nextjs.py` exige y ejecuta, desde el subdirectorio correcto, `npm run test`, `npm run lint` y `npm run build`. La incorporacion de Node a la CI remota sigue pendiente. |
| Media | `create-next-app` requiere un directorio destino vacio, mientras la plantilla ya ocupa la raiz. | El frontend se ubico en `interfaz/`; la decision es razonable pero no esta estandarizada. | Incorporar en la documentacion del stack frontend la convencion de subdirectorio y los comandos que deben ejecutarse desde ahi. |
| Media | Las identidades de ejecucion de Windows produjeron problemas de ACL al instalar y ejecutar dependencias. | Se requirio intervencion administrativa del usuario; la reejecucion elevada del validador frontend fue bloqueada al leer `.env.local`. No fue un defecto funcional de las Skills. | Mantener la leccion del piloto y agregar un diagnostico acotado al runbook, sin recomendar cambios masivos de permisos. |
| Media | PostgreSQL local exige instalacion, servicio y credenciales fuera del control del framework. | La integracion real depende de una precondicion manual y de secretos locales. | Explicitar esa precondicion en el flujo de piloto; conservar secretos solo en `.env` ignorado y no automatizar instalaciones sin autorizacion. |
| Media | Docker no esta instalado en el entorno de validacion MCP. | El `Dockerfile` y el lock existen, pero la imagen OCI no dispone aun de evidencia de build. | Se agrego un trabajo aislado que construye y prueba la imagen en CI; falta ejecutarlo al publicar la rama. |
| Baja | La URL posicional de MCP Inspector 2.5.0 y 2.4.0 permanecio esperando sin alcanzar el endpoint local. | Los intentos se interrumpieron y no se usaron como evidencia. | Corregido para 2.5.0 con `--server-url`: listo Tools, invoco la Tool y demostro idempotencia entre conexiones; mantener esa forma explicita en la guia. |

## Lectura de seguridad

Los pilotos no declaran una aplicacion expuesta. El API continua limitado a `127.0.0.1`; no tiene usuarios, datos sensibles ni requisitos de acceso confirmados. En consecuencia, autenticacion, autorizacion, TLS, CORS y controles de red no deben agregarse por presuncion ni darse por cubiertos. Cualquier paso de exposicion requiere primero actores, datos, limites de confianza y decisiones de autorizacion.

## Siguiente etapa recomendada

1. Corregido y probado el tratamiento de texto multilinea del inicializador: PowerShell debe usar configuracion JSON; la secuencia literal se rechaza.
2. Estandarizada la validacion del piloto frontend desde `interfaz/`; queda pendiente resolver las ACL del entorno antes de repetirla bajo la identidad que corresponda.
3. Revisar los cambios pendientes, ejecutar la CI remota solo con autorizacion expresa de publicacion y resolver procedencia/licencia antes de redistribuir o etiquetar una version `v1.0.0`.
