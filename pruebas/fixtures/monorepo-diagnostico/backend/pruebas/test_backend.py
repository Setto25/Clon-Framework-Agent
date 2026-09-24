from aplicacion import calcular_total


def test_calcula_total_esperado() -> None:
    """Detecta el fallo ficticio del modulo anidado."""
    assert calcular_total(2) == 4
