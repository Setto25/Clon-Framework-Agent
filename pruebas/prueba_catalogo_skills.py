#!/usr/bin/env python3
"""Comprueba el catalogo y la politica de seleccion de Skills."""

from __future__ import annotations

import importlib.util
import re
import unittest
from pathlib import Path
from types import ModuleType
from typing import Optional, cast


RAIZ_FRAMEWORK = Path(__file__).resolve().parent.parent
RUTA_CATALOGO = RAIZ_FRAMEWORK / "scripts" / "catalogo_skills.py"
RAIZ_SKILLS = RAIZ_FRAMEWORK / "plantilla" / ".agents" / "skills"
RUTA_README = RAIZ_FRAMEWORK / "README.md"
PATRON_CANTIDAD_SKILLS = re.compile(r"las (\d+) Skills")


def cargar_modulo() -> ModuleType:
    """Carga el catalogo desde su ruta sin alterar Python globalmente."""
    especificacion = importlib.util.spec_from_file_location("catalogo_skills", RUTA_CATALOGO)
    if especificacion is None or especificacion.loader is None:
        raise RuntimeError("No se pudo cargar scripts/catalogo_skills.py")
    modulo = importlib.util.module_from_spec(especificacion)
    especificacion.loader.exec_module(modulo)
    return modulo


class PruebasCatalogoSkills(unittest.TestCase):
    """Verifica descubrimiento, categorias y core automatico."""

    def test_descubre_veintitres_nombres_unicos(self) -> None:
        """Confirma que todo el almacen fuente permanezca disponible."""
        modulo = cargar_modulo()
        registros = cast(list[dict[str, object]], modulo.descubrir_skills(RAIZ_SKILLS))
        nombres = [cast(str, registro["nombre"]) for registro in registros]
        self.assertEqual(len(nombres), 23)
        self.assertEqual(len(set(nombres)), 23)

    def test_define_el_core_automatico_exacto(self) -> None:
        """Impide ampliar silenciosamente las Skills instaladas por defecto."""
        modulo = cargar_modulo()
        self.assertEqual(
            tuple(modulo.CORE_AUTOMATICO),
            ("cerrar-modulo", "lecciones-aprendidas", "optimizar-contexto", "probar-e2e"),
        )

    def test_clasifica_stacks_y_opcionales(self) -> None:
        """Confirma que el destino se derive de la ubicacion del catalogo."""
        modulo = cargar_modulo()
        registros = cast(list[dict[str, object]], modulo.descubrir_skills(RAIZ_SKILLS))
        por_nombre = {cast(str, registro["nombre"]): registro for registro in registros}
        self.assertEqual(por_nombre["fastapi-setup"]["categoria"], "stack")
        self.assertEqual(por_nombre["fastapi-setup"]["stack"], "backend-fastapi")
        self.assertEqual(por_nombre["seguridad-backend"]["categoria"], "core")
        self.assertFalse(por_nombre["seguridad-backend"]["automatica"])
        self.assertEqual(por_nombre["delegar-entre-agentes"]["categoria"], "opcional")
        self.assertIsNone(por_nombre["delegar-entre-agentes"]["stack"])

    def test_documentacion_refleja_el_catalogo_completo(self) -> None:
        """Impide que README y LEEME conserven cantidades o Skills obsoletas."""
        modulo = cargar_modulo()
        registros = cast(list[dict[str, object]], modulo.descubrir_skills(RAIZ_SKILLS))
        contenido_readme = RUTA_README.read_text(encoding="utf-8")
        cantidades = {int(valor) for valor in PATRON_CANTIDAD_SKILLS.findall(contenido_readme)}
        self.assertEqual(cantidades, {len(registros)})

        for registro in registros:
            nombre = cast(str, registro["nombre"])
            with self.subTest(documento="README.md", skill=nombre):
                self.assertIn(f"`{nombre}`", contenido_readme)

            stack = cast(Optional[str], registro["stack"])
            if stack is None:
                continue
            ruta_leeme = RAIZ_SKILLS / "stacks" / stack / "LEEME.md"
            contenido_leeme = ruta_leeme.read_text(encoding="utf-8")
            with self.subTest(documento=str(ruta_leeme), skill=nombre):
                self.assertIn(f"`{nombre}`", contenido_leeme)


if __name__ == "__main__":
    unittest.main()
