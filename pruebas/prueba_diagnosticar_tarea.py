#!/usr/bin/env python3
"""Verifica que el prediagnostico extrae fallos estructurados sin consumir API."""

from __future__ import annotations

import unittest

from scripts.diagnosticar_tarea import (
    analizar_fallos_node,
    analizar_fallos_unittest,
    buscar_candidatos,
    descubrir_ejecutores,
    formatear_contexto,
)

from pathlib import Path

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "desarrollo-web"


SALIDA_UNITTEST_EJEMPLO = """\
FF.F
======================================================================
FAIL: test_crea_una_tarea_normalizada (prueba_backend.PruebasBackend.test_crea_una_tarea_normalizada)
Exige un titulo limpio y un identificador incremental.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "pruebas/prueba_backend.py", line 27, in test_crea_una_tarea_normalizada
    self.assertEqual(respuesta.status_code, 201)
AssertionError: 405 != 201

======================================================================
FAIL: test_alterna_el_estado_de_una_tarea (prueba_backend.PruebasBackend.test_alterna_el_estado_de_una_tarea)
Cambia el estado y devuelve la representacion actualizada.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "pruebas/prueba_backend.py", line 41, in test_alterna_el_estado_de_una_tarea
    self.assertEqual(respuesta.status_code, 200)
AssertionError: 404 != 200

======================================================================
FAIL: test_rechaza_un_titulo_vacio (prueba_backend.PruebasBackend.test_rechaza_un_titulo_vacio)
Impide almacenar tareas sin contenido util.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "pruebas/prueba_backend.py", line 36, in test_rechaza_un_titulo_vacio
    self.assertEqual(respuesta.status_code, 422)
AssertionError: 405 != 422

----------------------------------------------------------------------
Ran 4 tests in 0.045s

FAILED (failures=3)
"""

SALIDA_NODE_EJEMPLO = """\
✖ la interfaz permite crear y filtrar tareas (5.0198ms)
✖ el cliente integra creacion y cambio de estado con la API (1.8177ms)
ℹ tests 2
ℹ pass 0
ℹ fail 2

✖ failing tests:

test at pruebas/prueba_frontend.mjs:7:1
✖ la interfaz permite crear y filtrar tareas (5.0198ms)
  AssertionError [ERR_ASSERTION]: The input did not match the regular expression /<form[^>]+id=["']formulario-tarea["']/i.
test at pruebas/prueba_frontend.mjs:17:1
✖ el cliente integra creacion y cambio de estado con la API (1.8177ms)
  AssertionError [ERR_ASSERTION]: The input did not match the regular expression /method\\s*:\\s*["']POST["']/i.
"""


class PruebasAnalisisUnittest(unittest.TestCase):
    """Comprueba la extraccion de fallos de unittest."""

    def test_extrae_tres_fallos(self) -> None:
        fallos = analizar_fallos_unittest(SALIDA_UNITTEST_EJEMPLO)
        self.assertEqual(len(fallos), 3)

    def test_primer_fallo_tiene_nombre_y_codigos(self) -> None:
        fallos = analizar_fallos_unittest(SALIDA_UNITTEST_EJEMPLO)
        primero = fallos[0]
        self.assertEqual(primero["nombre"], "test_crea_una_tarea_normalizada")
        self.assertEqual(primero["esperado"], "201")
        self.assertEqual(primero["obtenido"], "405")

    def test_segundo_fallo_tiene_linea(self) -> None:
        fallos = analizar_fallos_unittest(SALIDA_UNITTEST_EJEMPLO)
        segundo = fallos[1]
        self.assertEqual(segundo["linea"], 41)

    def test_salida_vacia_no_produce_fallos(self) -> None:
        fallos = analizar_fallos_unittest("")
        self.assertEqual(len(fallos), 0)

    def test_salida_aprobada_no_produce_fallos(self) -> None:
        salida = "....\n----------------------------------------------------------------------\nRan 4 tests in 0.047s\n\nOK"
        fallos = analizar_fallos_unittest(salida)
        self.assertEqual(len(fallos), 0)


class PruebasAnalisisNode(unittest.TestCase):
    """Comprueba la extraccion de fallos de node --test."""

    def test_extrae_dos_fallos(self) -> None:
        fallos = analizar_fallos_node(SALIDA_NODE_EJEMPLO)
        self.assertEqual(len(fallos), 2)

    def test_primer_fallo_tiene_nombre(self) -> None:
        fallos = analizar_fallos_node(SALIDA_NODE_EJEMPLO)
        self.assertEqual(fallos[0]["nombre"], "la interfaz permite crear y filtrar tareas")

    def test_salida_aprobada_no_produce_fallos(self) -> None:
        salida = "✔ test aprobado (1.0ms)\nℹ tests 1\nℹ pass 1\nℹ fail 0\n"
        fallos = analizar_fallos_node(salida)
        self.assertEqual(len(fallos), 0)


class PruebasDescubrimientoEjecutores(unittest.TestCase):
    """Verifica que el fixture de desarrollo web detecta ambos ejecutores."""

    @unittest.skipUnless(FIXTURE.is_dir(), "Fixture de desarrollo web ausente")
    def test_descubre_unittest_y_node(self) -> None:
        ejecutores = descubrir_ejecutores(FIXTURE)
        nombres = [e[0] for e in ejecutores]
        self.assertIn("unittest", nombres)
        self.assertIn("node", nombres)


class PruebasBusquedaResponsables(unittest.TestCase):
    """Verifica que se identifican archivos fuente candidatos."""

    @unittest.skipUnless(FIXTURE.is_dir(), "Fixture de desarrollo web ausente")
    def test_identifica_archivos_python_como_candidatos(self) -> None:
        fallos = analizar_fallos_unittest(SALIDA_UNITTEST_EJEMPLO)
        candidatos = buscar_candidatos(FIXTURE, fallos)
        self.assertTrue(len(candidatos) > 0)
        self.assertTrue(any("aplicacion.py" in r for r in candidatos))


class PruebasFormateoContexto(unittest.TestCase):
    """Comprueba que el contexto generado es compacto y util."""

    def test_aprobadas_genera_mensaje_corto(self) -> None:
        contexto = formatear_contexto(True, [], [], [])
        self.assertIn("aprobaron", contexto)
        self.assertLess(len(contexto), 100)

    def test_fallos_incluye_conteo_y_archivos(self) -> None:
        fallos = analizar_fallos_unittest(SALIDA_UNITTEST_EJEMPLO)
        contexto = formatear_contexto(
            False, fallos, ["backend/aplicacion.py"], []
        )
        self.assertIn("FALLOS_DETECTADOS: 3", contexto)
        self.assertIn("backend/aplicacion.py", contexto)
        self.assertIn("ARCHIVOS_CANDIDATOS", contexto)

    def test_contexto_incluye_esperado_y_obtenido(self) -> None:
        fallos = analizar_fallos_unittest(SALIDA_UNITTEST_EJEMPLO)
        contexto = formatear_contexto(False, fallos, [], [])
        self.assertIn("esperado=201", contexto)
        self.assertIn("obtenido=405", contexto)


if __name__ == "__main__":
    unittest.main()
