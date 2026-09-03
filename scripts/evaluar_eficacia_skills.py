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
VARIANTES_HISTORICAS: tuple[str, ...] = ("control", "skill")
VARIANTES_SISTEMA: tuple[str, ...] = ("control_puro", "indice", "skill")
VARIANTES_DESARROLLO: tuple[str, ...] = (
    "control_puro",
    "indice",
    "skill_adaptativa",
    "skill_extendida",
    "extendido_compacto",
)
VARIANTES_DESARROLLO_AUTORITATIVO: tuple[str, ...] = (
    "control_puro",
    "indice_autoritativo",
    "skill_adaptativa",
    "skill_extendida",
    "extendido_compacto",
)
VARIANTES_SELECTOR_PYTHON: tuple[str, ...] = (
    "control_puro",
    "indice_autoritativo",
    "selector_python_compacto",
)
VARIANTES_HERRAMIENTAS_EFICIENTES: tuple[str, ...] = ("herramientas_actuales", "herramientas_eficientes")
VARIANTES_INDICE_EFICIENTES: tuple[str, ...] = ("herramientas_actuales", "indice_con_herramientas_eficientes")
VARIANTES_ADMITIDAS: set[str] = set(
    VARIANTES_HISTORICAS
    + VARIANTES_SISTEMA
    + VARIANTES_DESARROLLO
    + VARIANTES_DESARROLLO_AUTORITATIVO
    + VARIANTES_SELECTOR_PYTHON
    + VARIANTES_HERRAMIENTAS_EFICIENTES
    + VARIANTES_INDICE_EFICIENTES
)


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
    mecanismos_activados: bool
    duracion_anomala: bool


class Criterios(TypedDict):
    """Representa los umbrales que determinan la aprobacion del experimento."""

    margen_no_inferioridad: float
    ahorro_minimo_tokens: float


class Metricas(TypedDict):
    """Resume las metricas agregadas de una variante."""

    ejecuciones: int
    ejecuciones_exitosas: int
    tasa_eficacia: float
    tokens_totales: int
    tokens_promedio: float
    tokens_por_exito: Optional[float]
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
    comparaciones: dict[str, float]
    comparacion_ahorro_valida: bool
    pares_exitosos: int
    ahorro_tokens_pareados: Optional[float]
    ahorro_tokens_por_exito: Optional[float]
    observaciones: list[str]
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
    if variante not in VARIANTES_ADMITIDAS:
        raise ValueError(
            f"ejecuciones[{posicion}].variante no pertenece a un experimento soportado"
        )
    exito = datos.get("exito")
    pruebas = datos.get("pruebas_aprobadas")
    if not isinstance(exito, bool) or not isinstance(pruebas, bool):
        raise ValueError(f"ejecuciones[{posicion}] debe declarar resultados booleanos")
    escenario_normalizado = escenario.strip()
    exige_mecanismos = escenario_normalizado in {
        "desarrollo-web-herramientas-eficientes-v2",
        "desarrollo-web-indice-eficiente-v1",
    }
    mecanismos = datos.get("mecanismos_activados", False)
    if exige_mecanismos and not isinstance(mecanismos, bool):
        raise ValueError(
            f"ejecuciones[{posicion}].mecanismos_activados debe ser booleano en v2"
        )
    if not isinstance(mecanismos, bool):
        mecanismos = False
    duracion_anomala = datos.get("duracion_anomala", False)
    if not isinstance(duracion_anomala, bool):
        duracion_anomala = False
    return Ejecucion(
        escenario=escenario_normalizado,
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
        mecanismos_activados=mecanismos,
        duracion_anomala=duracion_anomala,
    )


def cargar_experimento(
    ruta: Path,
) -> tuple[str, Criterios, list[Ejecucion], tuple[str, ...]]:
    """Valida el experimento y exige observaciones equivalentes entre variantes."""
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
    variantes_presentes = {ejecucion["variante"] for ejecucion in ejecuciones}
    if variantes_presentes == set(VARIANTES_HISTORICAS):
        variantes = VARIANTES_HISTORICAS
    elif variantes_presentes == set(VARIANTES_SISTEMA):
        variantes = VARIANTES_SISTEMA
    elif variantes_presentes == set(VARIANTES_DESARROLLO):
        variantes = VARIANTES_DESARROLLO
    elif variantes_presentes == set(VARIANTES_DESARROLLO_AUTORITATIVO):
        variantes = VARIANTES_DESARROLLO_AUTORITATIVO
    elif variantes_presentes == set(VARIANTES_SELECTOR_PYTHON):
        variantes = VARIANTES_SELECTOR_PYTHON
    elif variantes_presentes == set(VARIANTES_HERRAMIENTAS_EFICIENTES):
        variantes = VARIANTES_HERRAMIENTAS_EFICIENTES
    elif variantes_presentes == set(VARIANTES_INDICE_EFICIENTES):
        variantes = VARIANTES_INDICE_EFICIENTES
    else:
        raise ValueError(
            "El experimento debe contener control/skill, control_puro/indice/skill "
            "o variantes de desarrollo con indice autoritativo y selector Python"
        )
    claves_por_variante: dict[str, set[tuple[str, int]]] = {
        variante: set() for variante in variantes
    }
    for ejecucion in ejecuciones:
        clave = (ejecucion["escenario"], ejecucion["repeticion"])
        claves = claves_por_variante[ejecucion["variante"]]
        if clave in claves:
            raise ValueError(f"Ejecucion duplicada: {ejecucion['variante']} {clave}")
        claves.add(clave)
    referencia = claves_por_variante[variantes[0]]
    if any(claves_por_variante[variante] != referencia for variante in variantes[1:]):
        raise ValueError("Las variantes deben contener los mismos escenarios y repeticiones")
    return skill.strip(), Criterios(
        margen_no_inferioridad=margen,
        ahorro_minimo_tokens=ahorro,
    ), ejecuciones, variantes


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
        ejecuciones_exitosas=eficaces,
        tasa_eficacia=eficaces / cantidad,
        tokens_totales=sum(tokens),
        tokens_promedio=sum(tokens) / cantidad,
        tokens_por_exito=(sum(tokens) / eficaces) if eficaces else None,
        llamadas_herramientas_promedio=sum(
            ejecucion["llamadas_herramientas"] for ejecucion in seleccionadas
        ) / cantidad,
        duracion_promedio_segundos=sum(
            ejecucion["duracion_segundos"] for ejecucion in seleccionadas
        ) / cantidad,
        reintentos_promedio=sum(ejecucion["reintentos"] for ejecucion in seleccionadas) / cantidad,
    )


def calcular_ahorro(base: Metricas, tratamiento: Metricas, nombre: str) -> float:
    """Calcula el ahorro proporcional frente a una base con consumo observado."""
    if base["tokens_totales"] == 0:
        raise ValueError(f"{nombre} debe registrar al menos un token")
    return 1 - (tratamiento["tokens_totales"] / base["tokens_totales"])


def es_exitosa(ejecucion: Ejecucion) -> bool:
    """Determina si una ejecucion completo la tarea y su validacion."""
    return ejecucion["exito"] and ejecucion["pruebas_aprobadas"]


def calcular_metricas_pareadas(
    ejecuciones: list[Ejecucion],
    base_variante: str,
    tratamiento_variante: str,
) -> tuple[int, Optional[float]]:
    """Compara tokens solo en pares donde ambas variantes terminaron correctamente."""
    por_clave = {
        (ejecucion["escenario"], ejecucion["repeticion"], ejecucion["variante"]): ejecucion
        for ejecucion in ejecuciones
    }
    tokens_base = 0
    tokens_tratamiento = 0
    pares_exitosos = 0
    for escenario, repeticion, variante in por_clave:
        if variante != base_variante:
            continue
        base = por_clave[(escenario, repeticion, base_variante)]
        tratamiento = por_clave[(escenario, repeticion, tratamiento_variante)]
        if not es_exitosa(base) or not es_exitosa(tratamiento):
            continue
        pares_exitosos += 1
        tokens_base += base["tokens_entrada"] + base["tokens_salida"]
        tokens_tratamiento += tratamiento["tokens_entrada"] + tratamiento["tokens_salida"]
    if not pares_exitosos:
        return 0, None
    return pares_exitosos, 1 - (tokens_tratamiento / tokens_base)


def calcular_ahorro_por_exito(base: Metricas, tratamiento: Metricas) -> Optional[float]:
    """Calcula el ahorro observado por resultado exitoso, incluyendo intentos fallidos."""
    costo_base = base["tokens_por_exito"]
    costo_tratamiento = tratamiento["tokens_por_exito"]
    if costo_base is None or costo_tratamiento is None:
        return None
    return 1 - (costo_tratamiento / costo_base)


def evaluar(
    skill: str,
    criterios: Criterios,
    ejecuciones: list[Ejecucion],
    variantes: tuple[str, ...],
) -> Informe:
    """Aprueba solo cuando el sistema conserva eficacia y alcanza el ahorro exigido."""
    metricas = {variante: resumir(ejecuciones, variante) for variante in variantes}
    if variantes == VARIANTES_HERRAMIENTAS_EFICIENTES:
        control = metricas["herramientas_actuales"]
        selector = metricas["herramientas_eficientes"]
        base_variante = "herramientas_actuales"
        tratamiento_variante = "herramientas_eficientes"
        ahorro = calcular_ahorro(control, selector, "Las herramientas actuales")
        diferencia = selector["tasa_eficacia"] - control["tasa_eficacia"]
        comparaciones = {"ahorro_herramientas_eficientes_frente_actuales": ahorro, "diferencia_eficacia_herramientas_eficientes_frente_actuales": diferencia}
    elif variantes == VARIANTES_INDICE_EFICIENTES:
        control = metricas["herramientas_actuales"]
        tratamiento = metricas["indice_con_herramientas_eficientes"]
        base_variante = "herramientas_actuales"
        tratamiento_variante = "indice_con_herramientas_eficientes"
        ahorro = calcular_ahorro(control, tratamiento, "Las herramientas actuales")
        diferencia = tratamiento["tasa_eficacia"] - control["tasa_eficacia"]
        comparaciones = {
            "ahorro_indice_con_herramientas_eficientes_frente_actuales": ahorro,
            "diferencia_eficacia_indice_con_herramientas_eficientes_frente_actuales": diferencia,
        }
    elif variantes == VARIANTES_SELECTOR_PYTHON:
        control = metricas["control_puro"]
        indice = metricas["indice_autoritativo"]
        selector = metricas["selector_python_compacto"]
        base_variante = "control_puro"
        tratamiento_variante = "selector_python_compacto"
        ahorro = calcular_ahorro(control, selector, "El control puro")
        diferencia = selector["tasa_eficacia"] - control["tasa_eficacia"]
        comparaciones = {
            "ahorro_indice_autoritativo_frente_control_puro": calcular_ahorro(
                control, indice, "El control puro"
            ),
            "ahorro_selector_python_compacto_frente_indice": calcular_ahorro(
                indice, selector, "El indice autoritativo"
            ),
            "ahorro_selector_python_compacto_frente_control_puro": ahorro,
            "diferencia_eficacia_indice_autoritativo_frente_control_puro": (
                indice["tasa_eficacia"] - control["tasa_eficacia"]
            ),
            "diferencia_eficacia_selector_python_compacto_frente_indice": (
                selector["tasa_eficacia"] - indice["tasa_eficacia"]
            ),
            "diferencia_eficacia_selector_python_compacto_frente_control_puro": diferencia,
        }
    elif variantes in (VARIANTES_DESARROLLO, VARIANTES_DESARROLLO_AUTORITATIVO):
        control = metricas["control_puro"]
        nombre_indice = (
            "indice_autoritativo"
            if variantes == VARIANTES_DESARROLLO_AUTORITATIVO
            else "indice"
        )
        indice = metricas[nombre_indice]
        adaptativa = metricas["skill_adaptativa"]
        extendida = metricas["skill_extendida"]
        compacta = metricas["extendido_compacto"]
        base_variante = "control_puro"
        tratamiento_variante = "skill_adaptativa"
        ahorro = calcular_ahorro(control, adaptativa, "El control puro")
        diferencia = adaptativa["tasa_eficacia"] - control["tasa_eficacia"]
        comparaciones = {
            f"ahorro_{nombre_indice}_frente_control_puro": calcular_ahorro(
                control, indice, "El control puro"
            ),
            "ahorro_skill_adaptativa_frente_indice": calcular_ahorro(
                indice, adaptativa, f"La variante con {nombre_indice}"
            ),
            "ahorro_skill_extendida_frente_indice": calcular_ahorro(
                indice, extendida, f"La variante con {nombre_indice}"
            ),
            "ahorro_extendido_compacto_frente_indice": calcular_ahorro(
                indice, compacta, f"La variante con {nombre_indice}"
            ),
            "ahorro_skill_extendida_frente_adaptativa": calcular_ahorro(
                adaptativa, extendida, "La Skill adaptativa"
            ),
            "ahorro_extendido_compacto_frente_skill_extendida": calcular_ahorro(
                extendida, compacta, "La Skill extendida"
            ),
            "ahorro_sistema_adaptativo_frente_control_puro": ahorro,
            "ahorro_sistema_compacto_frente_control_puro": calcular_ahorro(
                control, compacta, "El control puro"
            ),
            f"diferencia_eficacia_{nombre_indice}_frente_control_puro": (
                indice["tasa_eficacia"] - control["tasa_eficacia"]
            ),
            "diferencia_eficacia_skill_adaptativa_frente_indice": (
                adaptativa["tasa_eficacia"] - indice["tasa_eficacia"]
            ),
            "diferencia_eficacia_skill_extendida_frente_adaptativa": (
                extendida["tasa_eficacia"] - adaptativa["tasa_eficacia"]
            ),
            "diferencia_eficacia_extendido_compacto_frente_indice": (
                compacta["tasa_eficacia"] - indice["tasa_eficacia"]
            ),
            "diferencia_eficacia_sistema_adaptativo_frente_control_puro": diferencia,
            "diferencia_eficacia_sistema_compacto_frente_control_puro": (
                compacta["tasa_eficacia"] - control["tasa_eficacia"]
            ),
        }
    elif variantes == VARIANTES_SISTEMA:
        control = metricas["control_puro"]
        indice = metricas["indice"]
        con_skill = metricas["skill"]
        base_variante = "control_puro"
        tratamiento_variante = "skill"
        ahorro = calcular_ahorro(control, con_skill, "El control puro")
        diferencia = con_skill["tasa_eficacia"] - control["tasa_eficacia"]
        comparaciones = {
            "ahorro_indice_frente_control_puro": calcular_ahorro(
                control, indice, "El control puro"
            ),
            "ahorro_skill_frente_indice": calcular_ahorro(
                indice, con_skill, "La variante con indice"
            ),
            "ahorro_sistema_frente_control_puro": ahorro,
            "diferencia_eficacia_indice_frente_control_puro": (
                indice["tasa_eficacia"] - control["tasa_eficacia"]
            ),
            "diferencia_eficacia_skill_frente_indice": (
                con_skill["tasa_eficacia"] - indice["tasa_eficacia"]
            ),
            "diferencia_eficacia_sistema_frente_control_puro": diferencia,
        }
    else:
        control = metricas["control"]
        con_skill = metricas["skill"]
        base_variante = "control"
        tratamiento_variante = "skill"
        ahorro = calcular_ahorro(control, con_skill, "El control")
        diferencia = con_skill["tasa_eficacia"] - control["tasa_eficacia"]
        comparaciones = {
            "ahorro_skill_frente_control": ahorro,
            "diferencia_eficacia_skill_frente_control": diferencia,
        }
    razones: list[str] = []
    pares_exitosos, ahorro_pareado = calcular_metricas_pareadas(
        ejecuciones, base_variante, tratamiento_variante
    )
    ahorro_por_exito = calcular_ahorro_por_exito(control, metricas[tratamiento_variante])
    comparacion_valida = (
        control["tasa_eficacia"] == 1.0
        and metricas[tratamiento_variante]["tasa_eficacia"] == 1.0
    )
    observaciones: list[str] = []
    if not comparacion_valida:
        observaciones.append(
            "El ahorro agregado incluye ejecuciones incompletas; no constituye una comparacion causal de ahorro."
        )
    if pares_exitosos == 0:
        observaciones.append(
            "No existen pares exitosos comparables para estimar ahorro condicionado al exito."
        )
    nombres = {
        "control": "El control",
        "control_puro": "El control puro",
        "indice": "La variante con indice",
        "indice_autoritativo": "La variante con indice autoritativo",
        "selector_python_compacto": "El selector Python compacto",
        "herramientas_actuales": "Las herramientas actuales",
        "herramientas_eficientes": "Las herramientas eficientes",
        "indice_con_herramientas_eficientes": "El indice con herramientas eficientes",
        "skill": "La Skill",
        "skill_adaptativa": "La Skill adaptativa",
        "skill_extendida": "La Skill en modo extendido",
        "extendido_compacto": "El protocolo extendido compacto",
    }
    for variante in variantes:
        if metricas[variante]["tasa_eficacia"] < 1.0:
            razones.append(
                f"{nombres[variante]} no satisface el criterio de eficacia en todas sus ejecuciones"
            )
    if diferencia < -criterios["margen_no_inferioridad"]:
        razones.append("La eficacia del tratamiento objetivo es inferior al margen permitido")
    if ahorro < criterios["ahorro_minimo_tokens"]:
        razones.append("El ahorro de tokens no alcanza el umbral requerido")
    if variantes == VARIANTES_HERRAMIENTAS_EFICIENTES and any(
        not ejecucion["mecanismos_activados"]
        for ejecucion in ejecuciones
        if ejecucion["variante"] == "herramientas_eficientes"
    ):
        razones.append("Las herramientas eficientes no activaron ningun mecanismo medible")
    if variantes == VARIANTES_INDICE_EFICIENTES and any(
        not ejecucion["mecanismos_activados"]
        for ejecucion in ejecuciones
        if ejecucion["variante"] == "indice_con_herramientas_eficientes"
    ):
        razones.append("El indice con herramientas eficientes no activo ningun mecanismo medible")
    if any(ejecucion["duracion_anomala"] for ejecucion in ejecuciones):
        razones.append("La duracion contiene una medicion anomala y no es comparable")
    return Informe(
        version=1,
        skill=skill,
        aprobada=not razones,
        ahorro_tokens=ahorro,
        diferencia_eficacia=diferencia,
        comparaciones=comparaciones,
        comparacion_ahorro_valida=comparacion_valida,
        pares_exitosos=pares_exitosos,
        ahorro_tokens_pareados=ahorro_pareado,
        ahorro_tokens_por_exito=ahorro_por_exito,
        observaciones=observaciones,
        razones=razones,
        variantes=metricas,
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
        skill, criterios, ejecuciones, variantes = cargar_experimento(argumentos.entrada)
        informe = evaluar(skill, criterios, ejecuciones, variantes)
        escribir_informe(argumentos.salida, informe)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0 if informe["aprobada"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
