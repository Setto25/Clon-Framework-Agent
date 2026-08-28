#!/usr/bin/env python3
"""Comprueba el catalogo y la politica de seleccion de Skills."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from types import ModuleType
from typing import cast


RAIZ_FRAMEWORK = Path(__file__).resolve().parent.parent
RUTA_CATALOGO = RAIZ_FRAMEWORK / "scripts" / "catalogo_skills.py"
RAIZ_SKILLS = RAIZ_FRAMEWORK / "plantilla" / ".agents" / "skills"


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

    def test_descubre_veinte_nombres_unicos(self) -> None:
        """Confirma que todo el almacen fuente permanezca disponible."""
        modulo = cargar_modulo()
        registros = cast(list[dict[str, object]], modulo.descubrir_skills(RAIZ_SKILLS))
        nombres = [cast(str, registro["nombre"]) for registro in registros]
        self.assertEqual(len(nombres), 20)
        self.assertEqual(len(set(nombres)), 20)

    def test_define_el_core_automatico_exacto(self) -> None:
        """Impide ampliar silenciosamente las Skills instaladas por defecto."""
        modulo = cargar_modulo()
        self.assertEqual(
            tuple(modulo.CORE_AUTOMATICO),
            ("cerrar-modulo", "lecciones-aprendidas", "probar-e2e"),
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


if __name__ == "__main__":
    unittest.main()
