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

    def test_conserva_las_veinticuatro_skills(self) -> None:
        """Confirma que la mejora no elimine ninguna Skill inventariada."""
        self.assertEqual(len(self.manifiestos), 24)

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

    def test_optimizacion_usa_carga_progresiva_y_escalamiento_observable(self) -> None:
        """Impide volver a cargar el protocolo costoso por una tarea comun."""
        raiz = RAIZ_SKILLS / "optimizar-contexto"
        manifiesto = (raiz / "SKILL.md").read_text(encoding="utf-8")
        modo_extendido = raiz / "referencias" / "modo_extendido.md"
        modo_arquitectonico = raiz / "referencias" / "modo_arquitectonico.md"
        self.assertTrue(modo_extendido.is_file())
        self.assertTrue(modo_arquitectonico.is_file())
        self.assertIn("referencias/modo_extendido.md", manifiesto)
        self.assertIn("referencias/modo_arquitectonico.md", manifiesto)
        self.assertIn("mas de 10 rutas o dos ciclos fallidos", manifiesto)
        self.assertIn("dos ciclos fallidos", manifiesto)
        self.assertIn("prever cuatro lecturas", manifiesto)
        self.assertIn("indice autoritativo", manifiesto)
        self.assertIn("no listes ni reconfirmes", manifiesto)
        self.assertLess(len(manifiesto.encode("utf-8")), 3200)

    def test_servidores_mcp_conservan_portabilidad_y_carga_progresiva(self) -> None:
        """Comprueba recursos, fronteras reemplazables y limites de autoridad."""
        raiz = RAIZ_SKILLS / "stacks" / "ia-llm" / "skills" / "desarrollar-servidores-mcp"
        manifiesto = (raiz / "SKILL.md").read_text(encoding="utf-8")
        referencias = {
            "arquitectura_servidor.md",
            "diseno_herramientas.md",
            "seguridad_autenticacion.md",
            "despliegue_portable.md",
            "pruebas_interoperabilidad.md",
        }
        rutas = {ruta.name for ruta in (raiz / "referencias").glob("*.md")}
        self.assertEqual(rutas, referencias)
        for nombre in referencias:
            with self.subTest(referencia=nombre):
                self.assertIn(f"referencias/{nombre}", manifiesto)
        self.assertIn("valores predeterminados reemplazables", manifiesto)
        self.assertIn("Negociar la version MCP", manifiesto)
        self.assertIn("autorizacion fuera del modelo", manifiesto)
        self.assertIn("autorizacion explicita", manifiesto)
        self.assertNotIn("Codex", manifiesto)
        self.assertLess(len(manifiesto.encode("utf-8")), 6500)


if __name__ == "__main__":
    unittest.main()
