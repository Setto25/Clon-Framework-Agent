"""Comprueba el comportamiento funcional solicitado al backend."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from backend.aplicacion import aplicacion
from backend.modelos import TAREAS


class PruebasBackend(unittest.TestCase):
    """Valida creacion, normalizacion y cambio de estado."""

    def setUp(self) -> None:
        """Restablece datos conocidos antes de cada caso."""
        TAREAS[:] = [
            {"id": 1, "titulo": "Revisar inventario", "completada": False},
            {"id": 2, "titulo": "Publicar informe", "completada": True},
        ]
        self.cliente = TestClient(aplicacion)

    def test_crea_una_tarea_normalizada(self) -> None:
        """Exige un titulo limpio y un identificador incremental."""
        respuesta = self.cliente.post("/api/tareas", json={"titulo": "  Preparar demo  "})
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(
            respuesta.json(),
            {"id": 3, "titulo": "Preparar demo", "completada": False},
        )

    def test_rechaza_un_titulo_vacio(self) -> None:
        """Impide almacenar tareas sin contenido util."""
        respuesta = self.cliente.post("/api/tareas", json={"titulo": "   "})
        self.assertEqual(respuesta.status_code, 422)

    def test_alterna_el_estado_de_una_tarea(self) -> None:
        """Cambia el estado y devuelve la representacion actualizada."""
        respuesta = self.cliente.patch("/api/tareas/1")
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.json()["completada"])

    def test_rechaza_un_identificador_desconocido(self) -> None:
        """Devuelve un error HTTP verificable para una tarea inexistente."""
        respuesta = self.cliente.patch("/api/tareas/999")
        self.assertEqual(respuesta.status_code, 404)


if __name__ == "__main__":
    unittest.main()
