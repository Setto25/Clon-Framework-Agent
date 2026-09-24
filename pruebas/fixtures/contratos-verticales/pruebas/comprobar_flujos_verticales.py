#!/usr/bin/env python3
"""Reproduce nueve regresiones verticales sin depender de un proyecto real."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ESCENARIO = Path(__file__).resolve().parent.parent / "escenario.json"


class PruebasFlujosVerticales(unittest.TestCase):
    """Comprueba contratos entre capas, transportes, datos y documentacion."""

    @classmethod
    def setUpClass(cls) -> None:
        """Carga el escenario ficticio una sola vez."""
        cls.datos = json.loads(ESCENARIO.read_text(encoding="utf-8"))

    def test_propaga_campo_hasta_servicio(self) -> None:
        """Exige que el endpoint entregue al servicio todos los campos aceptados."""
        flujo = self.datos["propagacion_campo"]
        self.assertEqual(set(flujo["frontend"]), set(flujo["schema"]))
        self.assertEqual(set(flujo["schema"]), set(flujo["endpoint_servicio"]))

    def test_actualiza_frontend_despues_de_mutacion(self) -> None:
        """Exige refresco o notificacion despues de persistir una mutacion."""
        flujo = self.datos["actualizacion_frontend"]
        self.assertTrue(not flujo["persistencia_confirmada"] or flujo["refresco"] or flujo["notificacion"])

    def test_mantiene_paridad_rest_websocket(self) -> None:
        """Exige el mismo contrato visible en REST y WebSocket."""
        flujo = self.datos["paridad_transportes"]
        self.assertEqual(set(flujo["rest"]), set(flujo["websocket"]))

    def test_no_fija_localhost_con_url_configurable(self) -> None:
        """Impide mezclar una URL configurable con llamadas locales fijas."""
        flujo = self.datos["urls"]
        self.assertTrue(all(llamada.startswith(flujo["configurable"]) for llamada in flujo["llamadas"]))

    def test_importacion_no_confirma_parcialmente(self) -> None:
        """Exige atomicidad antes de confirmar lotes importados."""
        flujo = self.datos["importacion"]
        self.assertTrue(flujo["atomica"] or "confirmacion_lote_1" not in flujo["eventos"])

    def test_schema_real_coincide_con_modelos(self) -> None:
        """Comprueba estructura real aunque la migracion figure en head."""
        flujo = self.datos["schema"]
        self.assertEqual(set(flujo["campos_modelo"]), set(flujo["campos_reales"]))

    def test_claves_foraneas_impiden_huerfanos(self) -> None:
        """Exige integridad referencial activa y ausencia de huerfanos."""
        flujo = self.datos["integridad"]
        self.assertTrue(flujo["claves_foraneas_activas"])
        self.assertEqual(flujo["registros_huerfanos"], 0)

    def test_plantilla_mapea_campos_visibles(self) -> None:
        """Exige mapeo para cada campo visible de la plantilla."""
        flujo = self.datos["plantilla"]
        self.assertEqual(set(flujo["campos_visibles"]), set(flujo["campos_mapeados"]))

    def test_documentacion_no_anticipa_puertas(self) -> None:
        """Impide declarar cierre mientras una puerta tenga codigo no cero."""
        flujo = self.datos["cierre"]
        aprobadas = all(codigo == 0 for codigo in flujo["puertas"].values())
        self.assertTrue(flujo["estado_documentado"] != "terminado" or aprobadas)


if __name__ == "__main__":
    unittest.main()


