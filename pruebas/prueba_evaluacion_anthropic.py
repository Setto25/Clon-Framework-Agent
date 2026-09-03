#!/usr/bin/env python3
"""Comprueba el adaptador Anthropic sin invocar servicios externos."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any


DEPENDENCIAS_DISPONIBLES = (
    importlib.util.find_spec("anthropic") is not None
    and importlib.util.find_spec("google.genai") is not None
)
if DEPENDENCIAS_DISPONIBLES:
    from scripts.analizar_impacto import analizar_impacto
    from scripts.evaluar_agente_anthropic import (
        MAXIMO_EJECUCIONES_HERRAMIENTAS,
        MAXIMO_TOKENS_SALIDA,
        MAXIMO_TURNOS,
        construir_instruccion,
        ejecutar_agente,
        uso,
    )
    from scripts.evaluar_agente_gemini import (
        RAIZ,
        TERMINOS_IMPACTO,
        construir_solicitud,
    )
    from scripts.validar_resultado_agente import (
        RUTAS_ESENCIALES_MIGRACION,
        crear_indice_con_requisitos,
    )
else:
    RAIZ = Path(__file__).resolve().parent.parent


class BloqueTextoFalso:
    """Representa un bloque minimo compatible con el SDK."""

    def __init__(self, texto: str) -> None:
        """Conserva el texto que devolvera la respuesta simulada."""
        self.texto = texto

    def model_dump(self, **_: object) -> dict[str, object]:
        """Serializa el bloque con el contrato esperado por el adaptador."""
        return {"type": "text", "text": self.texto}


class BloqueHerramientaFalso:
    """Representa una solicitud de lectura compatible con el SDK."""

    def __init__(self, identificador: str, inicio: int) -> None:
        """Conserva una lectura diferenciada por su linea inicial."""
        self.identificador = identificador
        self.inicio = inicio

    def model_dump(self, **_: object) -> dict[str, object]:
        """Serializa la llamada con el contrato esperado por el adaptador."""
        return {
            "type": "tool_use",
            "id": self.identificador,
            "name": "leer_archivo",
            "input": {"ruta": "README.md", "inicio": self.inicio, "limite": 1},
        }


class ClienteFalso:
    """Devuelve respuestas predefinidas mediante la interfaz messages.create."""

    def __init__(self, respuestas: list[object]) -> None:
        """Registra las respuestas que se consumiran en orden."""
        self.respuestas = respuestas
        self.messages = self
        self.ultima_solicitud: dict[str, object] = {}

    def create(self, **argumentos: object) -> object:
        """Extrae la siguiente respuesta sin realizar una solicitud externa."""
        self.ultima_solicitud = argumentos
        return self.respuestas.pop(0)


@unittest.skipUnless(
    DEPENDENCIAS_DISPONIBLES,
    "Los SDK opcionales de Anthropic y Gemini no estan instalados",
)
class PruebasEvaluacionAnthropic(unittest.TestCase):
    """Verifica tokens y rubrica con una respuesta Sonnet simulada."""

    def crear_auditoria_valida(self) -> str:
        """Construye una respuesta que cubre el contrato real del escenario."""
        rutas = sorted(RUTAS_ESENCIALES_MIGRACION)
        evidencias: list[dict[str, str]] = []
        for ruta in rutas[:6]:
            lineas = (RAIZ / ruta).read_text(encoding="utf-8").splitlines()
            patron = next(linea for linea in lineas if linea.strip())[:160]
            evidencias.append(
                {
                    "ruta": ruta,
                    "patron": patron,
                    "motivo": "Aporta evidencia literal comprobable",
                }
            )
        return json.dumps(
            {
                "rutas_afectadas": [
                    {"ruta": ruta, "cambio": "Actualizar la referencia"}
                    for ruta in rutas
                ],
                "evidencias": evidencias,
                "pruebas": [
                    {
                        "comando": "python scripts/catalogo_skills.py",
                        "motivo": "Comprueba el catalogo resultante",
                    }
                ],
                "riesgos": ["Puede permanecer una referencia obsoleta"],
            }
        )

    def test_suma_tokens_de_cache_como_entrada(self) -> None:
        """Incluye todas las categorias facturables del uso de entrada."""
        respuesta = SimpleNamespace(
            usage=SimpleNamespace(
                input_tokens=100,
                output_tokens=20,
                cache_creation_input_tokens=30,
                cache_read_input_tokens=40,
            )
        )
        self.assertEqual(uso(respuesta), (170, 20, 30, 40))

    def test_aprueba_una_respuesta_directa_sin_consumir_api(self) -> None:
        """Aplica el indice y la rubrica con un cliente completamente simulado."""
        respuesta = SimpleNamespace(
            content=[BloqueTextoFalso(self.crear_auditoria_valida())],
            stop_reason="end_turn",
            usage=SimpleNamespace(
                input_tokens=100,
                output_tokens=20,
                cache_creation_input_tokens=0,
                cache_read_input_tokens=0,
            ),
        )
        indice = crear_indice_con_requisitos(
            analizar_impacto(RAIZ, TERMINOS_IMPACTO),
            RUTAS_ESENCIALES_MIGRACION,
            RAIZ,
        )
        cliente_falso = ClienteFalso([respuesta])
        cliente: Any = cliente_falso
        resultado = ejecutar_agente(
            cliente,
            "sonnet-simulado",
            "indice",
            indice,
        )
        self.assertTrue(resultado["pruebas_aprobadas"])
        self.assertEqual(resultado["tokens_entrada"], 100)
        self.assertEqual(resultado["tokens_salida"], 20)
        self.assertEqual(resultado["llamadas_herramientas"], 0)
        self.assertEqual(resultado["razones_detencion"], ["end_turn"])
        self.assertNotIn("temperature", cliente_falso.ultima_solicitud)
        self.assertNotIn("tools", cliente_falso.ultima_solicitud)
        self.assertEqual(
            cliente_falso.ultima_solicitud["max_tokens"],
            MAXIMO_TOKENS_SALIDA,
        )

    def test_repara_un_truncamiento_antes_de_aplicar_la_rubrica(self) -> None:
        """Solicita un JSON completo cuando el proveedor corta la primera salida."""
        uso_falso = SimpleNamespace(
            input_tokens=100,
            output_tokens=20,
            cache_creation_input_tokens=0,
            cache_read_input_tokens=0,
        )
        truncada = SimpleNamespace(
            content=[BloqueTextoFalso('{"rutas_afectadas": [')],
            stop_reason="max_tokens",
            usage=uso_falso,
        )
        completa = SimpleNamespace(
            content=[BloqueTextoFalso(self.crear_auditoria_valida())],
            stop_reason="end_turn",
            usage=uso_falso,
        )
        indice = crear_indice_con_requisitos(
            analizar_impacto(RAIZ, TERMINOS_IMPACTO),
            RUTAS_ESENCIALES_MIGRACION,
            RAIZ,
        )
        resultado = ejecutar_agente(
            ClienteFalso([truncada, completa]),
            "sonnet-simulado",
            "indice",
            indice,
        )
        self.assertTrue(resultado["pruebas_aprobadas"])
        self.assertEqual(resultado["truncamientos"], 1)
        self.assertEqual(resultado["razones_detencion"], ["max_tokens", "end_turn"])
        self.assertEqual(len(resultado["historial_rubrica"]), 1)

    def test_limita_las_lecturas_adicionales(self) -> None:
        """Deshabilita herramientas despues de ejecutar el presupuesto permitido."""
        llamadas = [
            BloqueHerramientaFalso(f"lectura-{indice}", indice + 1)
            for indice in range(MAXIMO_EJECUCIONES_HERRAMIENTAS + 1)
        ]
        uso_falso = SimpleNamespace(
            input_tokens=100,
            output_tokens=20,
            cache_creation_input_tokens=0,
            cache_read_input_tokens=0,
        )
        respuesta_herramientas = SimpleNamespace(
            content=llamadas,
            stop_reason="tool_use",
            usage=uso_falso,
        )
        respuesta_final = SimpleNamespace(
            content=[BloqueTextoFalso(self.crear_auditoria_valida())],
            stop_reason="end_turn",
            usage=uso_falso,
        )
        indice = crear_indice_con_requisitos(
            analizar_impacto(RAIZ, TERMINOS_IMPACTO),
            RUTAS_ESENCIALES_MIGRACION,
            RAIZ,
        )
        cliente = ClienteFalso([respuesta_herramientas, respuesta_final])
        resultado = ejecutar_agente(
            cliente,
            "sonnet-simulado",
            "skill",
            indice,
        )
        self.assertTrue(resultado["pruebas_aprobadas"])
        self.assertEqual(
            resultado["ejecuciones_herramientas"],
            MAXIMO_EJECUCIONES_HERRAMIENTAS,
        )
        self.assertEqual(resultado["herramientas_rechazadas"], 1)
        self.assertNotIn("tools", cliente.ultima_solicitud)

    def test_control_puro_no_recibe_indice_ni_protocolo(self) -> None:
        """Separa el descubrimiento normal del preanalisis y de la Skill."""
        solicitud, indice_serializado = construir_solicitud("control_puro", None)
        instruccion = construir_instruccion("control_puro")
        self.assertEqual(indice_serializado, "")
        self.assertNotIn("INDICE_LOCAL_DE_IMPACTO", solicitud)
        self.assertNotIn("rutas_requeridas_en_rutas_afectadas", solicitud)
        self.assertIn("No recibes un indice previo", instruccion)
        self.assertIn("ni debes aplicar el protocolo", instruccion.casefold())

    def test_registra_fallo_si_no_emite_respuesta_final(self) -> None:
        """Conserva una ejecucion invalida sin abortar el experimento completo."""
        uso_falso = SimpleNamespace(
            input_tokens=100,
            output_tokens=20,
            cache_creation_input_tokens=0,
            cache_read_input_tokens=0,
        )
        respuestas = [
            SimpleNamespace(
                content=[BloqueHerramientaFalso(f"lectura-{indice}", indice + 1)],
                stop_reason="tool_use",
                usage=uso_falso,
            )
            for indice in range(MAXIMO_TURNOS)
        ]
        resultado = ejecutar_agente(
            ClienteFalso(respuestas),
            "sonnet-simulado",
            "control_puro",
            None,
        )
        self.assertFalse(resultado["exito"])
        self.assertFalse(resultado["pruebas_aprobadas"])
        self.assertIn("excedio el limite de turnos", resultado["rubrica_fallos"][0])

    def test_indice_excluye_skill_y_conserva_evidencia_local(self) -> None:
        """Aisla el valor del indice sin cargar instrucciones de la Skill."""
        indice = crear_indice_con_requisitos(
            analizar_impacto(RAIZ, TERMINOS_IMPACTO),
            RUTAS_ESENCIALES_MIGRACION,
            RAIZ,
        )
        solicitud, indice_serializado = construir_solicitud("indice", indice)
        instruccion = construir_instruccion("indice")
        self.assertTrue(indice_serializado)
        self.assertIn("INDICE_LOCAL_DE_IMPACTO", solicitud)
        self.assertIn("evidencias_disponibles", solicitud)
        self.assertIn("No apliques el protocolo", instruccion)
        self.assertIn("primer turno no tendras herramientas", instruccion)
        self.assertNotIn("# Optimizar contexto", instruccion)


if __name__ == "__main__":
    unittest.main()
