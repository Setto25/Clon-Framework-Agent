#!/usr/bin/env python3
"""Comprueba referencias y limites de los deltas para agentes."""

from __future__ import annotations

import unittest
from pathlib import Path


RAIZ_FRAMEWORK = Path(__file__).resolve().parent.parent
RAIZ_PLANTILLA = RAIZ_FRAMEWORK / "plantilla"
RAIZ_PROMPTS = RAIZ_PLANTILLA / "documentacion" / "prompts"
DELTAS: tuple[Path, ...] = (
    RAIZ_PROMPTS / "SYSTEM_PROMPT_DELTA_ANTIGRAVITY.md",
    RAIZ_PROMPTS / "SYSTEM_PROMPT_DELTA_CLAUDE.md",
    RAIZ_PROMPTS / "SYSTEM_PROMPT_DELTA_CODEX.md",
)


class PruebasCompatibilidadAgentes(unittest.TestCase):
    """Evita promesas absolutas y referencias locales inexistentes."""

    def test_existen_las_referencias_comunes(self) -> None:
        """Confirma que los archivos base citados formen parte de la plantilla."""
        esperados = (
            RAIZ_PLANTILLA / "AGENTS.md",
            RAIZ_PLANTILLA / "PROJECT_STATE.md",
            RAIZ_PLANTILLA / ".agents" / "rules" / "claude.md",
            RAIZ_PROMPTS / "SYSTEM_PROMPT_BASE.md",
            *DELTAS,
        )
        for ruta in esperados:
            with self.subTest(ruta=ruta):
                self.assertTrue(ruta.is_file())

    def test_no_reintroduce_capacidades_o_rutas_obsoletas(self) -> None:
        """Impide afirmar capacidades que dependen del producto o la sesion."""
        contenido = "\n".join(ruta.read_text(encoding="utf-8") for ruta in DELTAS)
        prohibidos = (
            "Antigravity (OpenAI)",
            "{{NOMBRE_PROYECTO}}_contexto.md",
            "Claude NO es un agente autónomo",
            "No descubre Skills automáticamente",
            "Las reglas en `.agents/rules/` se aplican automáticamente",
        )
        for fragmento in prohibidos:
            with self.subTest(fragmento=fragmento):
                self.assertNotIn(fragmento, contenido)


if __name__ == "__main__":
    unittest.main()
