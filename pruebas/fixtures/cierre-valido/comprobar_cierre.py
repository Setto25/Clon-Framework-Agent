"""Comprueba el comportamiento observable del fixture."""

from modulo import sumar


def main() -> int:
    """Devuelve un codigo distinto de cero cuando la suma no coincide."""
    return 0 if sumar(2, 3) == 5 else 1


if __name__ == "__main__":
    raise SystemExit(main())
