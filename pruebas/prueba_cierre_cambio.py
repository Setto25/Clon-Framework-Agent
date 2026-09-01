#!/usr/bin/env python3
"""Comprueba las puertas automaticas que impiden cierres incompletos."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.validar_cierre_cambio import (
    RAIZ,
    validar_dependencias_skills,
    validar_documentacion_cambio,
    validar_referencias_documentales,
)
from scripts.validar_contrato_plantilla import cargar_configuracion


class PruebasCierreCambio(unittest.TestCase):
    """Verifica dependencias, documentacion y registros operativos."""

    def test_dependencias_de_skills_existen_y_estan_administradas(self) -> None:
        """Impide que una Skill dependa de un script ausente al actualizar."""
        configuracion = cargar_configuracion(
            RAIZ / "plantilla" / "configuracion_plantilla.json"
        )
        errores = validar_dependencias_skills(
            set(configuracion["archivos_gestionados"])
        )
        self.assertEqual(errores, [])

    def test_documentacion_principal_no_cita_scripts_inexistentes(self) -> None:
        """Detecta nombres obsoletos en los documentos principales."""
        self.assertEqual(validar_referencias_documentales(), [])

    def test_cambio_material_exige_estado_y_readme(self) -> None:
        """Obliga a sincronizar ambos documentos en el mismo cambio."""
        errores = validar_documentacion_cambio(
            {"scripts/nuevo.py", "PROJECT_STATE.md"}
        )
        self.assertEqual(
            errores,
            ["Un cambio material no actualizo: README.md"],
        )
        self.assertEqual(
            validar_documentacion_cambio(
                {"scripts/nuevo.py", "PROJECT_STATE.md", "README.md"}
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
