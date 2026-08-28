#!/usr/bin/env python3
"""Comprueba invariantes estructurales y operativas de las Skills distribuidas."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


RAIZ_FRAMEWORK = Path(__file__).resolve().parent.parent
RAIZ_SKILLS = RAIZ_FRAMEWORK / "plantilla" / ".agents" / "skills"
PATRON_NOMBRE = re.compile(r"^name:\s*([^\r\n]+)$", re.MULTILINE)
PATRON_DESCRIPCION = re.compile(r"^description:\s*([^\r\n]+)$", re.MULTILINE)
PATRON_PLACEHOLDER = re.compile(r"\{\{[A-Z0-9_]+\}\}")
FRAGMENTOS_PROHIBIDOS: tuple[str, ...] = (
    "rm -rf",
    "git reset --hard",
    "catalogo_skills.json",
    "inicializar_proyecto.sh",
    "api_secret_key: str =",
    "cambiar-en-produccion",
    "DESCRIPCION_PRODUCTO_UNA_LINEA",
    "OBJETIVO_INMEDIATO",
    "EXCLUSIONES_MVP",
    "SECCION_ARQUITECTURA",
)


class PruebasCalidadSkills(unittest.TestCase):
    """Verifica que las Skills mantengan el contrato seguro acordado."""

    def setUp(self) -> None:
        """Localiza los manifiestos distribuidos."""
        self.manifiestos = sorted(RAIZ_SKILLS.rglob("SKILL.md"))

    def test_conserva_las_veinte_skills(self) -> None:
        """Confirma que la mejora no elimine ninguna Skill inventariada."""
        self.assertEqual(len(self.manifiestos), 20)

    def test_frontmatter_identifica_cada_carpeta(self) -> None:
        """Confirma nombre, descripcion y correspondencia con la carpeta."""
        for manifiesto in self.manifiestos:
            with self.subTest(ruta=manifiesto):
                contenido = manifiesto.read_text(encoding="utf-8")
                nombre = PATRON_NOMBRE.search(contenido)
                descripcion = PATRON_DESCRIPCION.search(contenido)
                self.assertIsNotNone(nombre)
                self.assertIsNotNone(descripcion)
                self.assertEqual(nombre.group(1).strip() if nombre else "", manifiesto.parent.name)
                self.assertTrue(descripcion.group(1).strip() if descripcion else "")

    def test_no_contiene_instrucciones_obsoletas_o_destructivas(self) -> None:
        """Impide reintroducir defectos operativos ya demostrados."""
        for manifiesto in self.manifiestos:
            contenido = manifiesto.read_text(encoding="utf-8")
            with self.subTest(ruta=manifiesto):
                self.assertEqual(PATRON_PLACEHOLDER.findall(contenido), [])
                for fragmento in FRAGMENTOS_PROHIBIDOS:
                    self.assertNotIn(fragmento, contenido)


if __name__ == "__main__":
    unittest.main()
