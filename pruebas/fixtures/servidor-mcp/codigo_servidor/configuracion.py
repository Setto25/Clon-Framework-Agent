"""Carga configuracion externa y falla de forma segura."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ConfiguracionServidor:
    """Agrupa la configuracion portable del servidor HTTP."""

    token_bearer: str
    url_emisor: str
    url_recurso: str
    hosts_permitidos: tuple[str, ...]
    maximo_cuerpo_bytes: int = 1_048_576

    @classmethod
    def desde_entorno(cls) -> "ConfiguracionServidor":
        """Construye la configuracion y rechaza secretos ausentes o debiles."""
        token = os.environ.get("MCP_TOKEN_BEARER", "")
        if len(token) < 32:
            raise RuntimeError("MCP_TOKEN_BEARER debe contener al menos 32 caracteres")
        url_emisor = os.environ.get("MCP_URL_EMISOR", "https://autenticacion.invalid")
        url_recurso = os.environ.get("MCP_URL_RECURSO", "http://127.0.0.1:8000/mcp")
        hosts = tuple(
            host.strip()
            for host in os.environ.get(
                "MCP_HOSTS_PERMITIDOS",
                "127.0.0.1,127.0.0.1:*,localhost,localhost:*",
            ).split(",")
            if host.strip()
        )
        if not hosts:
            raise RuntimeError("MCP_HOSTS_PERMITIDOS debe contener al menos un host")
        return cls(
            token_bearer=token,
            url_emisor=url_emisor,
            url_recurso=url_recurso,
            hosts_permitidos=hosts,
        )
