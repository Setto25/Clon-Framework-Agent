#!/usr/bin/env python3
"""Comprueba la rubrica factual de respuestas agenticas."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.validar_resultado_agente import (
    RUTAS_ESENCIALES_MIGRACION,
    crear_indice_con_requisitos,
    crear_retroalimentacion,
    evaluar_auditoria,
)


RAIZ_FRAMEWORK = Path(__file__).resolve().parent.parent


class PruebasValidacionResultadoAgente(unittest.TestCase):
    """Verifica rutas observadas, formato y comandos demostrables."""

    def setUp(self) -> None:
        """Crea un repositorio minimo con evidencia conocida."""
        self.temporal = tempfile.TemporaryDirectory(prefix="rubrica-agente-")
        self.raiz = Path(self.temporal.name)
        self.rutas = {f"modulo/archivo_{indice}.py" for indice in range(1, 7)}
        for ruta in self.rutas:
            archivo = self.raiz / ruta
            archivo.parent.mkdir(parents=True, exist_ok=True)
            archivo.write_text("pass\n", encoding="utf-8")

    def tearDown(self) -> None:
        """Elimina el repositorio temporal de la prueba."""
        self.temporal.cleanup()

    def crear_respuesta(self) -> str:
        """Construye una auditoria valida y completamente observada."""
        rutas = sorted(self.rutas)
        return json.dumps(
            {
                "rutas_afectadas": [
                    {"ruta": ruta, "cambio": "Actualizar referencia"} for ruta in rutas[:4]
                ],
                "evidencias": [
                    {
                        "ruta": ruta,
                        "patron": "pass",
                        "motivo": "Contiene una referencia comprobada",
                    }
                    for ruta in rutas
                ],
                "pruebas": [
                    {
                        "comando": "python modulo/archivo_1.py",
                        "motivo": "Comprueba el archivo afectado",
                    }
                ],
                "riesgos": ["Puede quedar una referencia obsoleta"],
            }
        )

    def test_aprueba_evidencia_existente_y_observada(self) -> None:
        """Aprueba cuando cada afirmacion factual posee respaldo local."""
        objeto, fallos = evaluar_auditoria(self.crear_respuesta(), self.raiz, self.rutas)
        self.assertIsNotNone(objeto)
        self.assertEqual(fallos, [])

    def test_aprueba_una_raiz_sin_canonizar(self) -> None:
        """Mantiene la comprobacion cuando la raiz contiene segmentos redundantes."""
        subdirectorio = self.raiz / "subdirectorio"
        subdirectorio.mkdir()
        raiz_sin_canonizar = subdirectorio / ".."
        objeto, fallos = evaluar_auditoria(
            self.crear_respuesta(), raiz_sin_canonizar, self.rutas
        )
        self.assertIsNotNone(objeto)
        self.assertEqual(fallos, [])

    def test_rechaza_ruta_inventada(self) -> None:
        """Rechaza una ruta aunque la respuesta conserve un JSON valido."""
        datos = json.loads(self.crear_respuesta())
        datos["evidencias"][0]["ruta"] = "plantilla/pruebas/inexistente.py"
        _, fallos = evaluar_auditoria(json.dumps(datos), self.raiz, self.rutas)
        self.assertTrue(any("inexistente" in fallo for fallo in fallos))

    def test_rechaza_comando_no_comprobable(self) -> None:
        """Rechaza un ejecutable que el contrato del proyecto no garantiza."""
        datos = json.loads(self.crear_respuesta())
        datos["pruebas"][0]["comando"] = "pytest modulo/archivo_1.py"
        _, fallos = evaluar_auditoria(json.dumps(datos), self.raiz, self.rutas)
        self.assertTrue(any("Comando no comprobable" in fallo for fallo in fallos))

    def test_rechaza_patron_que_no_aparece_en_archivo(self) -> None:
        """Rechaza una justificacion sin el fragmento literal declarado."""
        datos = json.loads(self.crear_respuesta())
        datos["evidencias"][0]["patron"] = "contenido inventado"
        _, fallos = evaluar_auditoria(json.dumps(datos), self.raiz, self.rutas)
        self.assertTrue(any("Patron no encontrado" in fallo for fallo in fallos))

    def test_rechaza_ruta_esencial_omitida(self) -> None:
        """Rechaza cobertura parcial aunque las rutas declaradas sean validas."""
        rutas = sorted(self.rutas)
        _, fallos = evaluar_auditoria(
            self.crear_respuesta(),
            self.raiz,
            self.rutas,
            {rutas[0], rutas[4]},
        )
        self.assertTrue(any("Faltan rutas esenciales" in fallo for fallo in fallos))

    def test_rechaza_violacion_del_protocolo(self) -> None:
        """Propaga una exploracion general como fallo de eficacia."""
        _, fallos = evaluar_auditoria(
            self.crear_respuesta(),
            self.raiz,
            self.rutas,
            violaciones_protocolo=["Se solicito un listado general de la raiz"],
        )
        self.assertIn("Se solicito un listado general de la raiz", fallos)

    def test_rutas_esenciales_del_escenario_existen(self) -> None:
        """Impide que la rubrica conserve rutas obsoletas o inventadas."""
        inexistentes = sorted(
            ruta for ruta in RUTAS_ESENCIALES_MIGRACION if not (RAIZ_FRAMEWORK / ruta).is_file()
        )
        self.assertEqual(inexistentes, [])

    def test_indice_publica_la_misma_cobertura_que_exige_la_rubrica(self) -> None:
        """Expone al agente todas las rutas que luego se comprobara que declare."""
        original: dict[str, object] = {"archivos": []}
        indice = crear_indice_con_requisitos(original, RUTAS_ESENCIALES_MIGRACION)
        self.assertEqual(
            indice["rutas_requeridas_en_rutas_afectadas"],
            sorted(RUTAS_ESENCIALES_MIGRACION),
        )
        self.assertNotIn("rutas_requeridas_en_rutas_afectadas", original)

    def test_retroalimentacion_conserva_los_fallos_sin_inventar_resultado(self) -> None:
        """Entrega al agente causas exactas y exige una respuesta de reemplazo."""
        mensaje = crear_retroalimentacion(["Falta README.md", "Comando no comprobable"])
        self.assertIn("Falta README.md", mensaje)
        self.assertIn("Comando no comprobable", mensaje)
        self.assertIn("JSON completo de reemplazo", mensaje)
        self.assertIn("especificamente a rutas_afectadas", mensaje)
        self.assertIn("subcadena literal exacta", mensaje)


if __name__ == "__main__":
    unittest.main()
