"""Adapta la identidad autenticada sin acoplarla al dominio."""

from __future__ import annotations

from typing import Protocol

from mcp.server.auth.middleware.auth_context import get_access_token

from codigo_servidor.dominio import Identidad


class ProveedorIdentidad(Protocol):
    """Define la identidad disponible para una invocacion."""

    def obtener(self) -> Identidad | None:
        """Devuelve la identidad actual o ausencia de autenticacion."""


class ProveedorIdentidadHttp:
    """Convierte el token HTTP verificado en una identidad de dominio."""

    def obtener(self) -> Identidad | None:
        """Normaliza sujeto y alcances desde el contexto del SDK."""
        token = get_access_token()
        if token is None:
            return None
        sujeto = token.subject or token.client_id
        return Identidad(sujeto=sujeto, alcances=frozenset(token.scopes))


class ProveedorIdentidadFija:
    """Entrega una identidad explicita para pruebas sin transporte HTTP."""

    def __init__(self, identidad: Identidad | None) -> None:
        """Conserva la identidad que entregara durante la prueba."""
        self._identidad = identidad

    def obtener(self) -> Identidad | None:
        """Devuelve la identidad configurada."""
        return self._identidad
