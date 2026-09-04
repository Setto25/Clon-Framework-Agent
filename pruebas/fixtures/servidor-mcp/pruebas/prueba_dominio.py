"""Comprueba reglas del dominio sin MCP ni red."""

from __future__ import annotations

import unittest

from codigo_servidor.dominio import (
    AlmacenContadoresMemoria,
    AutorizadorContadores,
    ErrorAutorizacion,
    ErrorConflictoIdempotencia,
    Identidad,
    ServicioContadores,
)


class PruebasDominio(unittest.TestCase):
    """Verifica autoridad e idempotencia del servicio."""

    def setUp(self) -> None:
        """Crea un servicio aislado para cada prueba."""
        self.servicio = ServicioContadores(AlmacenContadoresMemoria(), AutorizadorContadores())
        self.identidad = Identidad(
            sujeto="propietario",
            alcances=frozenset({"contadores:leer", "contadores:escribir"}),
        )

    def test_repite_incremento_sin_duplicar_efecto(self) -> None:
        """Conserva el primer resultado para una clave repetida."""
        primero = self.servicio.incrementar("principal", 3, "operacion-1", self.identidad)
        segundo = self.servicio.incrementar("principal", 3, "operacion-1", self.identidad)
        self.assertEqual(primero.valor, 3)
        self.assertEqual(segundo.valor, 3)
        self.assertEqual(primero.operacion_id, "operacion-1")
        self.assertTrue(segundo.repetida)

    def test_rechaza_reutilizacion_incompatible(self) -> None:
        """Impide asignar otros argumentos a una clave existente."""
        self.servicio.incrementar("principal", 3, "operacion-1", self.identidad)
        with self.assertRaises(ErrorConflictoIdempotencia):
            self.servicio.incrementar("principal", 4, "operacion-1", self.identidad)

    def test_rechaza_escritura_sin_alcance(self) -> None:
        """Impide mutar con una identidad de solo lectura."""
        identidad_lectora = Identidad(
            sujeto="lector",
            alcances=frozenset({"contadores:leer"}),
        )
        with self.assertRaises(ErrorAutorizacion):
            self.servicio.incrementar("principal", 1, "operacion-1", identidad_lectora)


if __name__ == "__main__":
    unittest.main()
