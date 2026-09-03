#!/usr/bin/env python3
"""Valida localmente una auditoria agentica sin usar otro modelo como juez."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional


PATRON_RUTA_COMANDO = re.compile(
    r"(?:[A-Za-z0-9_.-]+[\\/])+[A-Za-z0-9_.*?-]+(?:\.[A-Za-z0-9_-]+)?"
)
EJECUTABLES_COMPROBABLES: set[str] = {"git", "python", "python3"}
RUTAS_ESENCIALES_MIGRACION: set[str] = {
    "PROJECT_STATE.md",
    "README.md",
    "auditoria/inventario_skills.json",
    "experimentos/archivos_skill.txt",
    "plantilla/.agents/skills/opcional/LEEME.md",
    "plantilla/.agents/skills/optimizar-contexto/SKILL.md",
    "plantilla/AGENTS.md",
    "pruebas/prueba_actualizacion_proyecto.py",
    "pruebas/prueba_catalogo_skills.py",
    "pruebas/prueba_creacion_proyecto.py",
    "scripts/catalogo_skills.py",
    "scripts/evaluar_agente_gemini.py",
}


def crear_indice_con_requisitos(
    indice: dict[str, object],
    rutas_requeridas: set[str],
    raiz: Path | None = None,
) -> dict[str, object]:
    """Agrega cobertura y evidencia literal utilizable al indice comprobable."""
    enriquecido = dict(indice)
    rutas_ordenadas = sorted(rutas_requeridas)
    enriquecido["rutas_requeridas_en_rutas_afectadas"] = rutas_ordenadas
    if raiz is not None:
        evidencias: list[dict[str, str]] = []
        for ruta in rutas_ordenadas:
            archivo = resolver_ruta_regular(raiz, ruta)
            if archivo is None:
                continue
            try:
                lineas = archivo.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeError):
                continue
            patron = next((linea.strip() for linea in lineas if linea.strip()), "")
            if patron:
                evidencias.append({"ruta": ruta, "patron": patron[:160]})
        enriquecido["evidencias_disponibles"] = evidencias
    return enriquecido


def crear_retroalimentacion(fallos: list[str]) -> str:
    """Construye una solicitud acotada para corregir una respuesta rechazada."""
    detalle = "\n".join(f"- {fallo}" for fallo in fallos)
    return (
        "La rubrica local rechazo la respuesta por estos motivos:\n"
        f"{detalle}\n"
        "Corrige la auditoria y devuelve ahora un objeto JSON completo de reemplazo, "
        "sin explicar que inspeccionaras archivos. Si hay herramientas disponibles, "
        "usarlas solo para las rutas o patrones rechazados; si no las hay, usar "
        "exclusivamente la evidencia ya disponible. "
        "Agrega especificamente a rutas_afectadas cada ruta anunciada como faltante, "
        "aunque ya aparezca en evidencias o en el indice. Conserva la evidencia valida, "
        "copia cada patron como una subcadena literal exacta del indice o del archivo y "
        "recomienda solo comandos Python o Git soportados por el proyecto."
    )


def extraer_objeto_json(texto: str) -> dict[str, object]:
    """Extrae un unico objeto JSON incluso si aparece dentro de una cerca Markdown."""
    inicio = texto.find("{")
    fin = texto.rfind("}")
    if inicio < 0 or fin < inicio:
        raise ValueError("La respuesta no contiene un objeto JSON completo")
    objeto: object = json.loads(texto[inicio : fin + 1])
    if not isinstance(objeto, dict):
        raise ValueError("La respuesta JSON no es un objeto")
    return objeto


def normalizar_ruta(valor: str) -> str:
    """Normaliza una ruta relativa declarada por el agente."""
    return valor.strip().strip("`'\"").replace("\\", "/").removeprefix("./")


def resolver_ruta_regular(raiz: Path, ruta_relativa: str) -> Optional[Path]:
    """Resuelve una ruta regular confinada a la raiz canonica del repositorio."""
    ruta = Path(ruta_relativa)
    if ruta.is_absolute() or ".." in ruta.parts:
        return None
    raiz_resuelta = raiz.resolve()
    resuelta = (raiz_resuelta / ruta).resolve()
    if raiz_resuelta != resuelta and raiz_resuelta not in resuelta.parents:
        return None
    return resuelta if resuelta.is_file() else None


def ruta_regular_existe(raiz: Path, ruta_relativa: str) -> bool:
    """Comprueba una ruta regular confinada a la raiz del repositorio."""
    return resolver_ruta_regular(raiz, ruta_relativa) is not None


def validar_coleccion_rutas(
    nombre: str,
    valor: object,
    raiz: Path,
    observadas: set[str],
    minimo: int,
) -> list[str]:
    """Valida rutas existentes, observadas y acompañadas por una explicacion."""
    fallos: list[str] = []
    if not isinstance(valor, list) or len(valor) < minimo:
        return [f"{nombre} debe contener al menos {minimo} elementos"]
    rutas_unicas: set[str] = set()
    for indice, elemento in enumerate(valor, start=1):
        if not isinstance(elemento, dict):
            fallos.append(f"{nombre}[{indice}] no es un objeto")
            continue
        ruta_bruta = elemento.get("ruta")
        explicacion = elemento.get("cambio") if nombre == "rutas_afectadas" else elemento.get("motivo")
        if not isinstance(ruta_bruta, str) or not ruta_bruta.strip():
            fallos.append(f"{nombre}[{indice}] no declara una ruta")
            continue
        ruta = normalizar_ruta(ruta_bruta)
        rutas_unicas.add(ruta)
        if not ruta_regular_existe(raiz, ruta):
            fallos.append(f"Ruta inexistente o no regular: {ruta}")
        if ruta not in observadas:
            fallos.append(f"Ruta no observada mediante herramientas: {ruta}")
        if not isinstance(explicacion, str) or not explicacion.strip():
            fallos.append(f"{nombre}[{indice}] no explica su relevancia")
        if nombre == "evidencias":
            patron = elemento.get("patron")
            if not isinstance(patron, str) or not patron.strip() or len(patron) > 160:
                fallos.append(f"{nombre}[{indice}] no declara un patron literal valido")
            else:
                archivo = resolver_ruta_regular(raiz, ruta)
                if archivo is None:
                    continue
                try:
                    contenido = archivo.read_text(encoding="utf-8")
                except (OSError, UnicodeError):
                    fallos.append(f"No se pudo comprobar el patron en: {ruta}")
                else:
                    if patron.strip().casefold() not in contenido.casefold():
                        fallos.append(f"Patron no encontrado en {ruta}: {patron.strip()}")
    if len(rutas_unicas) < minimo:
        fallos.append(f"{nombre} no contiene {minimo} rutas unicas")
    return fallos


def validar_comando(comando: str, raiz: Path) -> list[str]:
    """Rechaza ejecutables no demostrables y rutas de comando inexistentes."""
    fallos: list[str] = []
    partes = comando.strip().split(maxsplit=1)
    if not partes or partes[0].casefold() not in EJECUTABLES_COMPROBABLES:
        fallos.append(f"Comando no comprobable con las herramientas del proyecto: {comando}")
    for coincidencia in PATRON_RUTA_COMANDO.findall(comando):
        ruta = normalizar_ruta(coincidencia)
        if "*" in ruta or "?" in ruta:
            if not any(raiz.glob(ruta)):
                fallos.append(f"Patron de ruta sin coincidencias en comando: {ruta}")
        elif not (raiz / ruta).exists():
            fallos.append(f"Ruta inexistente en comando: {ruta}")
    return fallos


def evaluar_auditoria(
    texto: str,
    raiz: Path,
    rutas_observadas: set[str],
    rutas_esenciales: set[str] | None = None,
    violaciones_protocolo: list[str] | None = None,
) -> tuple[dict[str, object] | None, list[str]]:
    """Aplica una rubrica factual a la respuesta del escenario de auditoria."""
    try:
        objeto = extraer_objeto_json(texto)
    except (ValueError, json.JSONDecodeError) as error:
        return None, [str(error)]
    observadas = {normalizar_ruta(ruta) for ruta in rutas_observadas}
    fallos = validar_coleccion_rutas(
        "rutas_afectadas", objeto.get("rutas_afectadas"), raiz, observadas, 4
    )
    rutas_declaradas = objeto.get("rutas_afectadas")
    declaradas = {
        normalizar_ruta(str(elemento.get("ruta")))
        for elemento in rutas_declaradas
        if isinstance(rutas_declaradas, list)
        and isinstance(elemento, dict)
        and isinstance(elemento.get("ruta"), str)
    } if isinstance(rutas_declaradas, list) else set()
    faltantes = sorted((rutas_esenciales or set()) - declaradas)
    if faltantes:
        fallos.append(f"Faltan rutas esenciales: {', '.join(faltantes)}")
    fallos.extend(
        validar_coleccion_rutas(
            "evidencias", objeto.get("evidencias"), raiz, observadas, 6
        )
    )
    pruebas = objeto.get("pruebas")
    if not isinstance(pruebas, list) or not pruebas:
        fallos.append("pruebas debe contener al menos un comando")
    else:
        for indice, prueba in enumerate(pruebas, start=1):
            if not isinstance(prueba, dict):
                fallos.append(f"pruebas[{indice}] no es un objeto")
                continue
            comando = prueba.get("comando")
            motivo = prueba.get("motivo")
            if not isinstance(comando, str) or not comando.strip():
                fallos.append(f"pruebas[{indice}] no declara un comando")
            else:
                fallos.extend(validar_comando(comando, raiz))
            if not isinstance(motivo, str) or not motivo.strip():
                fallos.append(f"pruebas[{indice}] no explica su motivo")
    riesgos = objeto.get("riesgos")
    if not isinstance(riesgos, list) or not riesgos or not all(
        isinstance(riesgo, str) and riesgo.strip() for riesgo in riesgos
    ):
        fallos.append("riesgos debe contener descripciones no vacias")
    fallos.extend(violaciones_protocolo or [])
    return objeto, list(dict.fromkeys(fallos))
