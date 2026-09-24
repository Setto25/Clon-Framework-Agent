#!/usr/bin/env python3
"""Simula pytest dentro del fixture para mantener la regresion autocontenida."""

from __future__ import annotations

from aplicacion import calcular_total


def main() -> int:
    """Reproduce un fallo con una traza y un codigo de salida observables."""
    if calcular_total(2) != 4:
        print("pruebas/test_backend.py:6: AssertionError: assert 3 == 4")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
