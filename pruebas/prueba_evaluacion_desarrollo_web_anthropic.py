#!/usr/bin/env python3
"""Comprueba el adaptador web Anthropic sin realizar solicitudes externas."""

from __future__ import annotations

import importlib.util
import unittest
from types import SimpleNamespace
from typing import Any


DEPENDENCIAS_DISPONIBLES = all(
    importlib.util.find_spec(modulo) is not None
    for modulo in ("anthropic", "google.genai", "fastapi", "httpx")
)

if DEPENDENCIAS_DISPONIBLES:
    from scripts.evaluar_desarrollo_web_anthropic import (
        HERRAMIENTAS,
        HERRAMIENTAS_SIN_LISTADO,
        MAXIMO_TOKENS_SALIDA,
        construir_instruccion_anthropic,
        herramientas_disponibles,
        solicitar,
        uso,
    )


class ClienteFalso:
    """Expone la interfaz minima de Messages API sin usar red."""

    def __init__(self, respuesta: object) -> None:
        """Conserva la respuesta configurada y la ultima solicitud."""
        self.respuesta = respuesta
        self.messages = self
        self.ultima_solicitud: dict[str, object] = {}

    def create(self, **argumentos: object) -> object:
        """Registra la solicitud y devuelve la respuesta predefinida."""
        self.ultima_solicitud = argumentos
        return self.respuesta


@unittest.skipUnless(
    DEPENDENCIAS_DISPONIBLES,
    "El adaptador opcional requiere anthropic, google-genai, FastAPI y httpx",
)
class PruebasEvaluacionDesarrolloWebAnthropic(unittest.TestCase):
    """Verifica el contrato local del evaluador Sonnet aislado."""

    def test_indice_autoritativo_retira_listado(self) -> None:
        """Impide duplicar la exploracion cubierta por el indice fresco."""
        instruccion = construir_instruccion_anthropic("indice_autoritativo")
        self.assertIn("evidencia autoritativa", instruccion)
        self.assertIn("no ejecutes listar_archivos", instruccion)
        self.assertEqual(herramientas_disponibles("control_puro"), HERRAMIENTAS)
        self.assertEqual(
            herramientas_disponibles("skill_adaptativa"), HERRAMIENTAS_SIN_LISTADO
        )

    def test_uso_conserva_cache_como_entrada(self) -> None:
        """Incluye categorias de cache sin alterar los tokens de salida."""
        respuesta = SimpleNamespace(
            usage=SimpleNamespace(
                input_tokens=120,
                output_tokens=45,
                cache_creation_input_tokens=30,
                cache_read_input_tokens=20,
            )
        )
        self.assertEqual(uso(respuesta), (170, 45, 30, 20))

    def test_solicitud_declara_herramientas_y_salida_acotada(self) -> None:
        """Conserva una solicitud compatible sin parametros retirados del SDK."""
        cliente_falso = ClienteFalso(SimpleNamespace())
        cliente: Any = cliente_falso
        respuesta, reintentos = solicitar(
            cliente,
            "sonnet-simulado",
            "Sistema",
            [{"role": "user", "content": "Prueba"}],
            HERRAMIENTAS_SIN_LISTADO,
        )
        self.assertIs(respuesta, cliente_falso.respuesta)
        self.assertEqual(reintentos, 0)
        self.assertEqual(cliente_falso.ultima_solicitud["max_tokens"], MAXIMO_TOKENS_SALIDA)
        self.assertEqual(cliente_falso.ultima_solicitud["tools"], HERRAMIENTAS_SIN_LISTADO)
        self.assertNotIn("temperature", cliente_falso.ultima_solicitud)


if __name__ == "__main__":
    unittest.main()
