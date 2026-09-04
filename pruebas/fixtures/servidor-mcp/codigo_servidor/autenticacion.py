"""Implementa el perfil bearer personal reemplazable del piloto."""

from __future__ import annotations

import secrets

from mcp.server.auth.provider import AccessToken, TokenVerifier


class VerificadorBearerPersonal(TokenVerifier):
    """Verifica una unica credencial personal inyectada por configuracion."""

    def __init__(self, token_esperado: str) -> None:
        """Conserva el secreto requerido sin incorporarlo al codigo fuente."""
        self._token_esperado = token_esperado

    async def verify_token(self, token: str) -> AccessToken | None:
        """Devuelve una identidad de alcance minimo para el token valido."""
        if not secrets.compare_digest(token, self._token_esperado):
            return None
        return AccessToken(
            token=token,
            client_id="propietario-piloto",
            subject="propietario-piloto",
            scopes=["contadores:leer", "contadores:escribir"],
        )
