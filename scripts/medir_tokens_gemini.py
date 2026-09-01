#!/usr/bin/env python3
"""Ejecuta una evaluacion pareada de contexto mediante Gemini API."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from google import genai
from google.genai import errors, types


RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
TAREA = (
    "Identifica los documentos que deben actualizarse cuando se agrega, elimina, "
    "mueve o renombra una Skill. Devuelve exclusivamente un objeto JSON con las "
    "claves obligatorios y condicionales. Cada elemento debe tener ruta y "
    "justificacion; cada elemento condicional debe incluir condicion. Separa las "
    "rutas obligatorias siempre de las condicionales, indica rutas exactas, no "
    "modifiques archivos y no inventes documentos."
)
RUTAS_OBLIGATORIAS = frozenset(
    {
        "project_state.md",
        "readme.md",
        "auditoria/inventario_skills.json",
        "pruebas/prueba_inventario_skills.py",
        "pruebas/prueba_calidad_skills.py",
        "pruebas/prueba_catalogo_skills.py",
    }
)


def leer_lista_archivos(ruta_lista: Path) -> list[Path]:
    """Lee rutas relativas y valida que pertenezcan al proyecto."""
    rutas: list[Path] = []

    for linea in ruta_lista.read_text(encoding="utf-8").splitlines():
        ruta_relativa = linea.strip()

        if not ruta_relativa or ruta_relativa.startswith("#"):
            continue

        ruta = (RAIZ_PROYECTO / ruta_relativa).resolve()

        if (ruta != RAIZ_PROYECTO and RAIZ_PROYECTO not in ruta.parents) or not ruta.is_file():
            raise ValueError(f"Ruta invalida o inexistente: {ruta_relativa}")

        rutas.append(ruta)

    if not rutas:
        raise ValueError(f"La lista no contiene archivos: {ruta_lista}")

    return rutas


def construir_contexto(rutas: list[Path]) -> str:
    """Construye un contexto trazable a partir de archivos seleccionados."""
    secciones: list[str] = []

    for ruta in rutas:
        ruta_relativa = ruta.relative_to(RAIZ_PROYECTO).as_posix()
        contenido = ruta.read_text(encoding="utf-8")
        secciones.append(f"--- ARCHIVO: {ruta_relativa} ---\n{contenido}")

    return "\n\n".join(secciones)


def obtener_entero(uso: Any, campo: str) -> int:
    """Obtiene un contador no negativo desde los metadatos de uso."""
    valor = getattr(uso, campo, None)

    if isinstance(valor, int) and valor >= 0:
        return valor

    return 0


def normalizar_ruta(valor: object) -> str:
    """Normaliza una ruta declarada por el modelo para compararla con la rubrica."""
    if not isinstance(valor, str):
        return ""
    return valor.strip().replace("\\", "/").lstrip("/").lower()


def obtener_elementos(datos: object, clave: str) -> list[dict[str, object]]:
    """Extrae elementos JSON con la estructura declarada por la tarea."""
    if not isinstance(datos, dict):
        return []
    elementos = datos.get(clave)
    if not isinstance(elementos, list):
        return []
    return [elemento for elemento in elementos if isinstance(elemento, dict)]


def contiene_condicional(
    elementos: list[dict[str, object]],
    ruta_esperada: str,
    palabras_condicion: tuple[str, ...],
) -> bool:
    """Comprueba una ruta condicional y las palabras que justifican su condicion."""
    for elemento in elementos:
        ruta = normalizar_ruta(elemento.get("ruta"))
        condicion = str(elemento.get("condicion", "")).lower()
        coincide_ruta = ruta == ruta_esperada or ruta.endswith(f"/{ruta_esperada}")
        if coincide_ruta and any(palabra in condicion for palabra in palabras_condicion):
            return True
    return False


def validar_rubrica(respuesta: str) -> tuple[bool, list[str]]:
    """Evalua rutas y condiciones factuales sin delegar la correccion a otro modelo."""
    try:
        datos: object = json.loads(respuesta)
    except json.JSONDecodeError:
        return False, ["La respuesta no contiene JSON valido"]

    obligatorios = obtener_elementos(datos, "obligatorios")
    condicionales = obtener_elementos(datos, "condicionales")
    rutas_obligatorias = {normalizar_ruta(elemento.get("ruta")) for elemento in obligatorios}
    faltantes = sorted(RUTAS_OBLIGATORIAS - rutas_obligatorias)
    errores = [f"Falta la ruta obligatoria: {ruta}" for ruta in faltantes]

    requisitos_condicionales = (
        ("leeme.md", ("stack",)),
        ("atribuciones.md", ("extern", "procedencia", "fuente")),
        ("plantilla/agents.md", ("core",)),
        ("plantilla/.agents/rules/excepciones_nominales.md", ("nombre", "idioma", "tecn")),
    )
    for ruta, palabras in requisitos_condicionales:
        if not contiene_condicional(condicionales, ruta, palabras):
            errores.append(f"Falta o no condiciona correctamente: {ruta}")

    return not errores, errores


def ejecutar_variante(
    cliente: genai.Client,
    modelo: str,
    variante: str,
    repeticion: int,
    contexto: str,
    maximo_reintentos: int,
) -> dict[str, object]:
    """Ejecuta una variante y conserva sus metricas observables."""
    solicitud = (
        "Usa exclusivamente el siguiente contexto para resolver la tarea.\n\n"
        f"{contexto}\n\n"
        f"TAREA:\n{TAREA}"
    )
    inicio = time.perf_counter()
    reintentos = 0

    while True:
        try:
            respuesta = cliente.models.generate_content(
                model=modelo,
                contents=solicitud,
                config=types.GenerateContentConfig(
                    temperature=0,
                    max_output_tokens=1200,
                    response_mime_type="application/json",
                ),
            )
            break
        except errors.ServerError as error:
            if reintentos >= maximo_reintentos:
                raise RuntimeError(
                    f"Gemini no estuvo disponible tras {reintentos} reintentos: {error}"
                ) from error
            espera = 5 * (2**reintentos)
            reintentos += 1
            print(
                f"Gemini no esta disponible para {variante} {repeticion}; "
                f"se reintentara en {espera} segundos ({reintentos}/{maximo_reintentos})."
            )
            time.sleep(espera)

    duracion = time.perf_counter() - inicio
    uso = respuesta.usage_metadata
    tokens_entrada = obtener_entero(uso, "prompt_token_count")
    tokens_respuesta = obtener_entero(uso, "candidates_token_count")
    tokens_razonamiento = obtener_entero(uso, "thoughts_token_count")
    tokens_totales_api = obtener_entero(uso, "total_token_count")
    texto_respuesta = respuesta.text or ""
    pruebas_aprobadas, fallos_rubrica = validar_rubrica(texto_respuesta)

    return {
        "escenario": "actualizacion-documentacion-skills",
        "repeticion": repeticion,
        "variante": variante,
        "exito": True,
        "pruebas_aprobadas": pruebas_aprobadas,
        "tokens_entrada": tokens_entrada,
        "tokens_salida": tokens_respuesta + tokens_razonamiento,
        "tokens_respuesta": tokens_respuesta,
        "tokens_razonamiento": tokens_razonamiento,
        "tokens_totales_api": tokens_totales_api,
        "llamadas_herramientas": 0,
        "duracion_segundos": round(duracion, 3),
        "reintentos": reintentos,
        "rubrica_fallos": fallos_rubrica,
        "respuesta": texto_respuesta,
    }


def escribir_json(ruta: Path, contenido: dict[str, object]) -> None:
    """Escribe resultados mediante reemplazo atomico."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_name(f".{ruta.name}.temporal")

    try:
        with temporal.open("w", encoding="utf-8", newline="\n") as flujo:
            json.dump(contenido, flujo, ensure_ascii=False, indent=2)
            flujo.write("\n")
        os.replace(temporal, ruta)
    finally:
        if temporal.exists():
            temporal.unlink()


def crear_argumentos() -> argparse.Namespace:
    """Define argumentos para ejecutar una evaluacion reproducible."""
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument(
        "--modelo",
        default="gemini-3.7-flash",
        help="Modelo Gemini habilitado para la clave local.",
    )
    analizador.add_argument(
        "--repeticiones",
        type=int,
        default=3,
        help="Cantidad de ejecuciones por variante.",
    )
    analizador.add_argument(
        "--salida",
        type=Path,
        default=Path("resultados/evaluacion_optimizar_contexto_gemini.json"),
        help="Archivo JSON de resultados.",
    )
    analizador.add_argument(
        "--maximo-reintentos",
        type=int,
        default=3,
        help="Reintentos ante indisponibilidad temporal de Gemini.",
    )
    return analizador.parse_args()


def main() -> int:
    """Ejecuta variantes y publica datos pendientes de revision humana."""
    argumentos = crear_argumentos()

    if argumentos.repeticiones < 1 or argumentos.maximo_reintentos < 0:
        raise ValueError("repeticiones debe ser mayor que cero y maximo-reintentos no negativo")

    clave = os.environ.get("GEMINI_API_KEY")

    if not clave:
        raise ValueError("GEMINI_API_KEY no esta definida en esta terminal")

    cliente = genai.Client(api_key=clave)
    rutas_control = leer_lista_archivos(RAIZ_PROYECTO / "experimentos" / "archivos_control.txt")
    rutas_skill = leer_lista_archivos(RAIZ_PROYECTO / "experimentos" / "archivos_skill.txt")
    contexto_control = construir_contexto(rutas_control)
    contexto_skill = construir_contexto(rutas_skill)
    ejecuciones: list[dict[str, object]] = []

    for repeticion in range(1, argumentos.repeticiones + 1):
        print(f"Ejecutando control {repeticion}/{argumentos.repeticiones}...")
        ejecuciones.append(
            ejecutar_variante(
                cliente,
                argumentos.modelo,
                "control",
                repeticion,
                contexto_control,
                argumentos.maximo_reintentos,
            )
        )
        print(f"Ejecutando skill {repeticion}/{argumentos.repeticiones}...")
        ejecuciones.append(
            ejecutar_variante(
                cliente,
                argumentos.modelo,
                "skill",
                repeticion,
                contexto_skill,
                argumentos.maximo_reintentos,
            )
        )

    resultado: dict[str, object] = {
        "version": 1,
        "skill": "optimizar-contexto",
        "proveedor": "gemini-api",
        "modelo": argumentos.modelo,
        "criterios": {
            "margen_no_inferioridad": 0.0,
            "ahorro_minimo_tokens": 0.2,
        },
        "ejecuciones": ejecuciones,
    }
    escribir_json(argumentos.salida, resultado)
    print(f"Resultado guardado en: {argumentos.salida}")
    print("La rubrica factual marco automaticamente las respuestas aprobadas.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
