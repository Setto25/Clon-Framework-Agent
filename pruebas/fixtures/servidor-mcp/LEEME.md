# Fixture de servidor MCP

Este fixture valida la Skill `desarrollar-servidores-mcp` sin formar parte del catalogo distribuible. Usa el SDK oficial `mcp==2.1.1`, negocia MCP 2026-07-28 y expone el mismo servidor mediante cliente en memoria y Streamable HTTP.

## Capacidades

- `consultar_contador`: Tool de solo lectura.
- `incrementar_contador`: Tool mutable con clave idempotente.
- autenticacion bearer personal mediante `TokenVerifier` reemplazable;
- autorizacion por alcance dentro del servicio, separada de la autenticacion;
- proteccion de hosts y limite de cuerpo para el transporte HTTP;
- compatibilidad HTTP sin sesion para clientes MCP anteriores a 2026-07-28;
- aplicacion ASGI y contenedor OCI sin dependencia de Cloud Run.

El almacenamiento en memoria sirve solamente para el piloto de una replica. Sustituirlo por persistencia compartida antes de prometer durabilidad o escalamiento horizontal.

## Verificacion

Desde este directorio:

```powershell
uv sync --python 3.13 --frozen
uv run python -m unittest discover -s pruebas -p "prueba_*.py"
uv run python -m pruebas.probar_http_local
```

La prueba HTTP comprueba `/salud`, tokens ausente e invalido, host rechazado, cuerpo excesivo, descubrimiento de ambas Tools, mutacion autenticada y negociacion de protocolo. No crea recursos cloud ni consume APIs externas.

Con el servidor manual activo, un segundo cliente se valida mediante MCP Inspector:

```powershell
npm exec --yes --package=@modelcontextprotocol/inspector@2.5.0 -- mcp-inspector --cli --server-url http://127.0.0.1:8000/mcp --transport http --method tools/list --header "Authorization: Bearer <TOKEN>" --format json
```

En la validacion del fixture, el cliente Python negocio MCP 2026-07-28 e Inspector negocio 2025-11-25. El perfil `stateless_http=True` permite atender ambos sin afinidad de sesion; las funciones avanzadas que necesiten canal servidor-cliente requieren otra decision explicita.

## Ejecucion manual

Configurar las variables descritas en el proyecto piloto y ejecutar:

```powershell
uv run uvicorn codigo_servidor.entrada_http:aplicacion --host 127.0.0.1 --port 8000
```

Para un dominio remoto se deben sustituir `MCP_URL_RECURSO` y `MCP_HOSTS_PERMITIDOS`. La imagen usa `PORT`, por lo que el mismo artefacto puede ejecutarse en Cloud Run u otra plataforma compatible con contenedores.
