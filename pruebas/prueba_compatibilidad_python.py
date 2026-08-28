#!/usr/bin/env python3
"""Comprueba compatibilidad sintactica y coherencia entre validadores Python."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path


RAIZ_FRAMEWORK = Path(__file__).resolve().parent.parent
INICIALIZADOR = RAIZ_FRAMEWORK / "plantilla" / "scripts" / "inicializar_proyecto.py"
CREADOR = RAIZ_FRAMEWORK / "scripts" / "crear_proyecto.py"
VALIDADOR = RAIZ_FRAMEWORK / "scripts" / "validar_contrato_plantilla.py"


def evaluar_constante(nodo: ast.AST) -> object:
    """Evalua el subconjunto de expresiones usado por las constantes compartidas."""
    if isinstance(nodo, ast.Constant):
        return nodo.value
    if isinstance(nodo, ast.Set):
        return {evaluar_constante(elemento) for elemento in nodo.elts}
    if isinstance(nodo, ast.Tuple):
        return tuple(evaluar_constante(elemento) for elemento in nodo.elts)
    if isinstance(nodo, ast.List):
        return [evaluar_constante(elemento) for elemento in nodo.elts]
    if isinstance(nodo, ast.BinOp) and isinstance(nodo.op, ast.Mult):
        izquierdo = evaluar_constante(nodo.left)
        derecho = evaluar_constante(nodo.right)
        if isinstance(izquierdo, int) and isinstance(derecho, int):
            return izquierdo * derecho
    if (
        isinstance(nodo, ast.Call)
        and isinstance(nodo.func, ast.Name)
        and nodo.func.id == "frozenset"
        and len(nodo.args) == 1
        and not nodo.keywords
    ):
        valor = evaluar_constante(nodo.args[0])
        if isinstance(valor, (set, tuple, list)):
            return frozenset(valor)
    raise AssertionError(f"Expresion constante no soportada: {ast.dump(nodo)}")


def extraer_constantes(ruta: Path, nombres: frozenset[str]) -> dict[str, object]:
    """Extrae constantes declaradas sin importar ni ejecutar el modulo inspeccionado."""
    arbol = ast.parse(ruta.read_text(encoding="utf-8"), filename=str(ruta), feature_version=9)
    resultado: dict[str, object] = {}
    for nodo in arbol.body:
        nombre: str | None = None
        valor: ast.AST | None = None
        if isinstance(nodo, ast.Assign) and len(nodo.targets) == 1:
            objetivo = nodo.targets[0]
            if isinstance(objetivo, ast.Name):
                nombre = objetivo.id
                valor = nodo.value
        elif isinstance(nodo, ast.AnnAssign) and isinstance(nodo.target, ast.Name):
            nombre = nodo.target.id
            valor = nodo.value
        if nombre in nombres and valor is not None:
            resultado[nombre] = evaluar_constante(valor)
    faltantes = nombres - set(resultado)
    if faltantes:
        raise AssertionError(f"{ruta} no declara las constantes: {', '.join(sorted(faltantes))}")
    return resultado


class PruebasCompatibilidadPython(unittest.TestCase):
    """Verifica el piso declarado de Python y las reglas deliberadamente duplicadas."""

    def test_todo_el_codigo_acepta_la_gramatica_de_python_39(self) -> None:
        """Analiza cada modulo con la gramatica correspondiente a Python 3.9."""
        archivos = sorted(RAIZ_FRAMEWORK.rglob("*.py"))
        self.assertTrue(archivos)
        for archivo in archivos:
            with self.subTest(archivo=archivo.relative_to(RAIZ_FRAMEWORK)):
                contenido = archivo.read_text(encoding="utf-8")
                arbol = ast.parse(contenido, filename=str(archivo), feature_version=9)
                for nodo in ast.walk(arbol):
                    if not isinstance(nodo, ast.Call) or not isinstance(nodo.func, ast.Attribute):
                        continue
                    if (
                        isinstance(nodo.func.value, ast.Name)
                        and nodo.func.value.id == "ast"
                        and nodo.func.attr == "walk"
                    ):
                        continue
                    argumentos = {palabra.arg for palabra in nodo.keywords}
                    self.assertFalse(
                        nodo.func.attr == "write_text" and "newline" in argumentos,
                        f"{archivo} usa Path.write_text(newline=), no disponible en Python 3.9",
                    )
                    self.assertFalse(
                        nodo.func.attr == "chmod" and "follow_symlinks" in argumentos,
                        f"{archivo} usa Path.chmod(follow_symlinks=), no portable en Python 3.9",
                    )
                    self.assertNotIn(
                        nodo.func.attr,
                        {"walk", "is_junction"},
                        f"{archivo} usa Path.{nodo.func.attr}(), posterior a Python 3.9",
                    )

    def test_mantiene_coherencia_en_constantes_duplicadas(self) -> None:
        """Impide que el validador, el creador y la copia autonoma diverjan en silencio."""
        constantes_contrato = frozenset(
            {
                "VERSION_CONTRATO_SOPORTADA",
                "SINTAXIS_PLACEHOLDER_SOPORTADA",
                "ORIGENES_PERMITIDOS",
                "CLAVES_CONTRATO",
                "CLAVES_CAMPO_PLACEHOLDER",
                "MAXIMO_BYTES_JSON",
            }
        )
        self.assertEqual(
            extraer_constantes(VALIDADOR, constantes_contrato),
            extraer_constantes(INICIALIZADOR, constantes_contrato),
        )

        constantes_arbol = frozenset(
            {
                "MAXIMO_ENTRADAS_ARBOL",
                "MAXIMO_BYTES_TOTALES",
                "MAXIMO_BYTES_ARCHIVO",
                "NOMBRES_ARTEFACTOS_GENERADOS",
                "SUFIJOS_ARTEFACTOS_GENERADOS",
            }
        )
        self.assertEqual(
            extraer_constantes(CREADOR, constantes_arbol),
            extraer_constantes(INICIALIZADOR, constantes_arbol),
        )


if __name__ == "__main__":
    unittest.main()
