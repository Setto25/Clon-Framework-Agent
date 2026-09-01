#!/usr/bin/env python3
"""Compara ejecuciones pareadas con y sin una Skill sin inventar mediciones."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional, TypedDict, cast


MAXIMO_BYTES_ENTRADA = 1024 * 1024
VARIANTES: tuple[str, ...] = ("control", "skill")


class Ejecucion(TypedDict):
    """Representa una observacion obtenida durante un experimento real."""

    escenario: str
    repeticion: int
    variante: str
    exito: bool
    pruebas_aprobadas: bool
    tokens_entrada: int
    tokens_salida: int
    llamadas_herramientas: int
    duracion_segundos: float
    reintentos: int


class Criterios(TypedDict):
    """Representa los umbrales que determinan la aprobacion del experimento."""

    margen_no_inferioridad: float
    ahorro_minimo_tokens: float


class Metricas(TypedDict):
    """Resume las metricas agregadas de una variante."""

    ejecuciones: int
    tasa_eficacia: float
    tokens_totales: int
    tokens_promedio: float
    llamadas_herramientas_promedio: float
    duracion_promedio_segundos: float
    reintentos_promedio: float


class Informe(TypedDict):
    """Representa la conclusion reproducible de una evaluacion."""

    version: int
    skill: str
    aprobada: bool
    ahorro_tokens: float
    diferencia_eficacia: float
    razones: list[str]
    variantes: dict[str, Metricas]


def exigir_numero_no_negativo(valor: object, campo: str) -> float:
    """Valida una metrica numerica no negativa sin admitir booleanos."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor < 0:
        raise ValueError(f"{campo} debe ser un numero no negativo")
    return float(valor)


def exigir_entero_no_negativo(valor: object, campo: str) -> int:
    """Valida una metrica entera no negativa."""
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
        raise ValueError(f"{campo} debe ser un entero no negativo")
    return valor


def cargar_json_acotado(ruta: Path) -> dict[str, object]:
    """Carga un objeto JSON regular dentro del limite permitido."""
    if not ruta.is_file() or ruta.stat().st_size > MAXIMO_BYTES_ENTRADA:
        raise ValueError("La entrada no existe, no es regular o supera 1 MiB")
    try:
        datos: object = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"No se pudo leer la evaluacion: {error}") from error
    if not isinstance(datos, dict):
        raise ValueError("La evaluacion debe ser un objeto JSON")
    return cast(dict[str, object], datos)


def validar_ejecucion(datos: object, posicion: int) -> Ejecucion:
    """Valida una ejecucion sin completar silenciosamente campos ausentes."""
    if not isinstance(datos, dict):
        raise ValueError(f"ejecuciones[{posicion}] debe ser un objeto")
    escenario = datos.get("escenario")
    variante = datos.get("variante")
    if not isinstance(escenario, str) or not escenario.strip():
        raise ValueError(f"ejecuciones[{posicion}].escenario debe contener texto")
    if variante not in VARIANTES:
        raise ValueError(f"ejecuciones[{posicion}].variante debe ser control o skill")
    exito = datos.get("exito")
    pruebas = datos.get("pruebas_aprobadas")
    if not isinstance(exito, bool) or not isinstance(pruebas, bool):
        raise ValueError(f"ejecuciones[{posicion}] debe declarar resultados booleanos")
    return Ejecucion(
        escenario=escenario.strip(),
        repeticion=exigir_entero_no_negativo(datos.get("repeticion"), "repeticion"),
        variante=cast(str, variante),
        exito=exito,
        pruebas_aprobadas=pruebas,
        tokens_entrada=exigir_entero_no_negativo(datos.get("tokens_entrada"), "tokens_entrada"),
        tokens_salida=exigir_entero_no_negativo(datos.get("tokens_salida"), "tokens_salida"),
        llamadas_herramientas=exigir_entero_no_negativo(
            datos.get("llamadas_herramientas"), "llamadas_herramientas"
        ),
        duracion_segundos=exigir_numero_no_negativo(
            datos.get("duracion_segundos"), "duracion_segundos"
        ),
        reintentos=exigir_entero_no_negativo(datos.get("reintentos"), "reintentos"),
    )


def cargar_experimento(ruta: Path) -> tuple[str, Criterios, list[Ejecucion]]:
    """Valida el experimento y exige pares equivalentes entre variantes."""
    datos = cargar_json_acotado(ruta)
    if datos.get("version") != 1:
        raise ValueError("La version de evaluacion soportada es 1")
    skill = datos.get("skill")
    if not isinstance(skill, str) or not skill.strip():
        raise ValueError("skill debe contener un nombre")
    criterios_crudos = datos.get("criterios")
    if not isinstance(criterios_crudos, dict):
        raise ValueError("criterios debe ser un objeto")
    margen = exigir_numero_no_negativo(
        criterios_crudos.get("margen_no_inferioridad"), "margen_no_inferioridad"
    )
    ahorro = exigir_numero_no_negativo(
        criterios_crudos.get("ahorro_minimo_tokens"), "ahorro_minimo_tokens"
    )
    if margen > 1 or ahorro > 1:
        raise ValueError("Los umbrales proporcionales deben quedar entre 0 y 1")
    ejecuciones_crudas = datos.get("ejecuciones")
    if not isinstance(ejecuciones_crudas, list) or not ejecuciones_crudas:
        raise ValueError("ejecuciones debe contener observaciones")
    ejecuciones = [
        validar_ejecucion(ejecucion, posicion)
        for posicion, ejecucion in enumerate(ejecuciones_crudas)
    ]
    claves_por_variante: dict[str, set[tuple[str, int]]] = {variante: set() for variante in VARIANTES}
    for ejecucion in ejecuciones:
        clave = (ejecucion["escenario"], ejecucion["repeticion"])
        claves = claves_por_variante[ejecucion["variante"]]
        if clave in claves:
            raise ValueError(f"Ejecucion duplicada: {ejecucion['variante']} {clave}")
        claves.add(clave)
    if claves_por_variante["control"] != claves_por_variante["skill"]:
        raise ValueError("Las variantes deben contener los mismos escenarios y repeticiones")
    return skill.strip(), Criterios(
        margen_no_inferioridad=margen,
        ahorro_minimo_tokens=ahorro,
    ), ejecuciones


def resumir(ejecuciones: list[Ejecucion], variante: str) -> Metricas:
    """Calcula metricas agregadas para una variante validada."""
    seleccionadas = [ejecucion for ejecucion in ejecuciones if ejecucion["variante"] == variante]
    cantidad = len(seleccionadas)
    eficaces = sum(
        1 for ejecucion in seleccionadas if ejecucion["exito"] and ejecucion["pruebas_aprobadas"]
    )
    tokens = [ejecucion["tokens_entrada"] + ejecucion["tokens_salida"] for ejecucion in seleccionadas]
    return Metricas(
        ejecuciones=cantidad,
        tasa_eficacia=eficaces / cantidad,
        tokens_totales=sum(tokens),
        tokens_promedio=sum(tokens) / cantidad,
        llamadas_herramientas_promedio=sum(
            ejecucion["llamadas_herramientas"] for ejecucion in seleccionadas
        ) / cantidad,
        duracion_promedio_segundos=sum(
            ejecucion["duracion_segundos"] for ejecucion in seleccionadas
        ) / cantidad,
        reintentos_promedio=sum(ejecucion["reintentos"] for ejecucion in seleccionadas) / cantidad,
    )


def evaluar(skill: str, criterios: Criterios, ejecuciones: list[Ejecucion]) -> Informe:
    """Aprueba solo cuando conserva eficacia y alcanza el ahorro exigido."""
    control = resumir(ejecuciones, "control")
    con_skill = resumir(ejecuciones, "skill")
    if control["tokens_totales"] == 0:
        raise ValueError("El control debe registrar al menos un token")
    ahorro = 1 - (con_skill["tokens_totales"] / control["tokens_totales"])
    diferencia = con_skill["tasa_eficacia"] - control["tasa_eficacia"]
    razones: list[str] = []
    if control["tasa_eficacia"] < 1.0:
        razones.append("El control no satisface el criterio de eficacia en todas sus ejecuciones")
    if con_skill["tasa_eficacia"] < 1.0:
        razones.append("La Skill no satisface el criterio de eficacia en todas sus ejecuciones")
    if diferencia < -criterios["margen_no_inferioridad"]:
        razones.append("La eficacia de la Skill es inferior al margen permitido")
    if ahorro < criterios["ahorro_minimo_tokens"]:
        razones.append("El ahorro de tokens no alcanza el umbral requerido")
    return Informe(
        version=1,
        skill=skill,
        aprobada=not razones,
        ahorro_tokens=ahorro,
        diferencia_eficacia=diferencia,
        razones=razones,
        variantes={"control": control, "skill": con_skill},
    )


def escribir_informe(ruta: Optional[Path], informe: Informe) -> None:
    """Publica el informe en salida estandar o mediante reemplazo atomico."""
    contenido = json.dumps(informe, ensure_ascii=False, indent=2) + "\n"
    if ruta is None:
        sys.stdout.write(contenido)
        return
    destino = ruta.expanduser().resolve()
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_name(f".{destino.name}.temporal")
    if temporal.exists():
        raise ValueError(f"Existe un informe temporal pendiente: {temporal}")
    try:
        with temporal.open("w", encoding="utf-8", newline="\n") as flujo:
            flujo.write(contenido)
        os.replace(temporal, destino)
    finally:
        if temporal.exists():
            temporal.unlink()


def crear_argumentos() -> argparse.Namespace:
    """Define la interfaz de evaluacion reproducible."""
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("entrada", type=Path, help="Experimento JSON con ejecuciones reales")
    analizador.add_argument("--salida", type=Path, help="Ruta opcional del informe JSON")
    return analizador.parse_args()


def main() -> int:
    """Evalua un experimento y diferencia rechazo de entrada invalida."""
    argumentos = crear_argumentos()
    try:
        skill, criterios, ejecuciones = cargar_experimento(argumentos.entrada)
        informe = evaluar(skill, criterios, ejecuciones)
        escribir_informe(argumentos.salida, informe)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0 if informe["aprobada"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
