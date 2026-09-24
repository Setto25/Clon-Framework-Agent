#!/usr/bin/env python3
"""Comprueba referencias y limites de los deltas para agentes."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


RAIZ_FRAMEWORK = Path(__file__).resolve().parent.parent
RAIZ_PLANTILLA = RAIZ_FRAMEWORK / "plantilla"
RAIZ_PROMPTS = RAIZ_PLANTILLA / "documentacion" / "prompts"
DELTAS: tuple[Path, ...] = (
    RAIZ_PROMPTS / "SYSTEM_PROMPT_DELTA_ANTIGRAVITY.md",
    RAIZ_PROMPTS / "SYSTEM_PROMPT_DELTA_CLAUDE.md",
    RAIZ_PROMPTS / "SYSTEM_PROMPT_DELTA_CODEX.md",
    RAIZ_PROMPTS / "SYSTEM_PROMPT_DELTA_CURSOR.md",
)
DOCUMENTOS_INTEROPERABLES: tuple[Path, ...] = (
    RAIZ_PLANTILLA / "AGENTS.md",
    RAIZ_PLANTILLA / "CLAUDE.md",
    RAIZ_PLANTILLA / ".agents" / "rules" / "00-contexto-framework.md",
    RAIZ_PLANTILLA / ".agents" / "rules" / "claude.md",
    RAIZ_PLANTILLA / ".agents" / "rules" / "excepciones_nominales.md",
    RAIZ_PLANTILLA / "documentacion" / "INDICE_LECTURA_AGENTES.md",
    RAIZ_PROMPTS / "SYSTEM_PROMPT_BASE.md",
    *DELTAS,
)


class PruebasCompatibilidadAgentes(unittest.TestCase):
    """Evita promesas absolutas y referencias locales inexistentes."""

    def test_existen_las_referencias_comunes(self) -> None:
        """Confirma que los archivos base citados formen parte de la plantilla."""
        esperados = (
            RAIZ_PLANTILLA / "AGENTS.md",
            RAIZ_PLANTILLA / "CLAUDE.md",
            RAIZ_PLANTILLA / "PROJECT_STATE.md",
            RAIZ_PLANTILLA / ".agents" / "rules" / "00-contexto-framework.md",
            RAIZ_PLANTILLA / ".agents" / "rules" / "claude.md",
            RAIZ_PROMPTS / "SYSTEM_PROMPT_BASE.md",
            *DELTAS,
        )
        for ruta in esperados:
            with self.subTest(ruta=ruta):
                self.assertTrue(ruta.is_file())

    def test_no_reintroduce_capacidades_o_rutas_obsoletas(self) -> None:
        """Impide afirmar capacidades que dependen del producto o la sesion."""
        contenido = "\n".join(
            ruta.read_text(encoding="utf-8")
            for ruta in DOCUMENTOS_INTEROPERABLES
        )
        prohibidos = (
            "Antigravity (OpenAI)",
            "Antigravity exige",
            "{{NOMBRE_PROYECTO}}_contexto.md",
            "Claude NO es un agente autónomo",
            "No descubre Skills automáticamente",
            "Las reglas en `.agents/rules/` se aplican automáticamente",
            "Se aplica automaticamente en cada sesion",
            "porque las herramientas exigen esas rutas",
            "documentacion/analisis/",
        )
        for fragmento in prohibidos:
            with self.subTest(fragmento=fragmento):
                self.assertNotIn(fragmento, contenido)

    def test_referencias_condicionales_tienen_fuente(self) -> None:
        """Confirma que stacks y Skills citados puedan instalarse desde la fuente."""
        raiz_skills = RAIZ_PLANTILLA / ".agents" / "skills"
        referencias_fijas = (
            raiz_skills / "cerrar-modulo" / "SKILL.md",
            raiz_skills / "evaluar-agente" / "SKILL.md",
            raiz_skills / "iniciar-proyecto" / "SKILL.md",
            raiz_skills / "opcional" / "delegar-entre-agentes" / "SKILL.md",
        )
        for referencia in referencias_fijas:
            with self.subTest(referencia=referencia):
                self.assertTrue(referencia.is_file())

        raiz_stacks = raiz_skills / "stacks"
        raiz_lecciones = raiz_skills / "lecciones-aprendidas" / "referencias"
        for stack in sorted(ruta for ruta in raiz_stacks.iterdir() if ruta.is_dir()):
            with self.subTest(stack=stack.name):
                self.assertTrue((stack / "LEEME.md").is_file())
                self.assertTrue((raiz_lecciones / f"{stack.name}.md").is_file())

    def test_puente_opencode_usa_la_fuente_canonica(self) -> None:
        """Comprueba que opencode descubra las Skills sin duplicar sus instrucciones."""
        puente = json.loads(
            (RAIZ_PLANTILLA / "opencode.json").read_text(encoding="utf-8")
        )
        self.assertEqual(puente.get("$schema"), "https://opencode.ai/config.json")
        self.assertEqual(puente.get("skills", {}).get("paths"), [".agents/skills"])

    def test_los_puentes_conservan_una_fuente_canonica(self) -> None:
        """Comprueba imports de Claude y reglas base sin duplicar las Skills."""
        claude = (RAIZ_PLANTILLA / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("@AGENTS.md", claude)
        self.assertIn("@PROJECT_STATE.md", claude)
        self.assertIn("@.agents/rules/claude.md", claude)
        regla = (
            RAIZ_PLANTILLA / ".agents" / "rules" / "00-contexto-framework.md"
        ).read_text(encoding="utf-8")
        self.assertIn("`AGENTS.md`", regla)
        self.assertIn("`PROJECT_STATE.md`", regla)
        self.assertIn("trigger: always_on", regla)
        self.assertIn("--solo-verificaciones", regla)

if __name__ == "__main__":
    unittest.main()
