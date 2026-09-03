#!/usr/bin/env python3
"""Comprueba el adaptador Qwen sin realizar solicitudes externas."""

from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any


DEPENDENCIAS_DISPONIBLES = all(
    importlib.util.find_spec(modulo) is not None
    for modulo in ("openai", "google.genai", "fastapi", "httpx")
)

if DEPENDENCIAS_DISPONIBLES:
    from scripts.evaluar_desarrollo_web_qwen import (
        FIXTURE,
        HERRAMIENTAS,
        HERRAMIENTAS_EFICIENTES,
        HERRAMIENTAS_SIN_LISTADO,
        MAXIMO_TOKENS_SALIDA,
        construir_instruccion_qwen,
        construir_solicitud_selector,
        ejecutar_herramienta_eficiente,
        ejecutar_agente,
        herramientas_disponibles,
        preparar_contexto_herramientas_eficientes,
        solicitar,
        solicitud_herramientas_eficientes,
        uso,
    )


class ClienteFalso:
    """Expone la interfaz minima de Chat Completions sin usar la red."""

    def __init__(self, respuesta: object) -> None:
        """Conserva una respuesta y los argumentos de la ultima solicitud."""
        self.respuestas = list(respuesta) if isinstance(respuesta, list) else [respuesta]
        self.chat = self
        self.completions = self
        self.ultima_solicitud: dict[str, object] = {}

    def create(self, **argumentos: object) -> object:
        """Devuelve la respuesta configurada y registra el contrato solicitado."""
        self.ultima_solicitud = argumentos
        return self.respuestas.pop(0)


@unittest.skipUnless(
    DEPENDENCIAS_DISPONIBLES,
    "El adaptador opcional requiere openai, google-genai, FastAPI y httpx",
)
class PruebasEvaluacionQwen(unittest.TestCase):
    """Verifica uso y parametros sin consumir cuota de Model Studio."""

    def test_registra_razonamiento_sin_sumarlo_dos_veces(self) -> None:
        """Conserva el razonamiento como desglose de la salida ya facturada."""
        respuesta = SimpleNamespace(
            usage=SimpleNamespace(
                prompt_tokens=120,
                completion_tokens=45,
                completion_tokens_details=SimpleNamespace(reasoning_tokens=30),
            )
        )
        self.assertEqual(uso(respuesta), (120, 45, 30))

    def test_solicitud_desactiva_razonamiento_y_declara_herramientas(self) -> None:
        """Mantiene comparables las variantes y no presupone thinking gratuito."""
        respuesta = SimpleNamespace()
        cliente_falso = ClienteFalso(respuesta)
        cliente: Any = cliente_falso
        obtenida, reintentos = solicitar(
            cliente,
            "qwen-simulado",
            [{"role": "user", "content": "Prueba"}],
            HERRAMIENTAS,
            False,
        )
        self.assertIs(obtenida, respuesta)
        self.assertEqual(reintentos, 0)
        self.assertEqual(cliente_falso.ultima_solicitud["max_completion_tokens"], MAXIMO_TOKENS_SALIDA)
        self.assertEqual(
            cliente_falso.ultima_solicitud["extra_body"],
            {"enable_thinking": False},
        )
        self.assertIn("tools", cliente_falso.ultima_solicitud)

    def test_solicitud_omite_herramientas_cuando_corresponde(self) -> None:
        """Permite cerrar una respuesta cuando el presupuesto se agota."""
        cliente_falso = ClienteFalso(SimpleNamespace())
        cliente: Any = cliente_falso
        solicitar(
            cliente,
            "qwen-simulado",
            [{"role": "user", "content": "Prueba"}],
            None,
            True,
        )
        self.assertNotIn("tools", cliente_falso.ultima_solicitud)
        self.assertEqual(
            cliente_falso.ultima_solicitud["extra_body"],
            {"enable_thinking": True},
        )

    def test_indice_autoritativo_retira_listado_y_declara_su_vigencia(self) -> None:
        """Impide que el preanalisis se duplique mediante una herramienta general."""
        instrucciones = construir_instruccion_qwen("indice_autoritativo")
        self.assertIn("evidencia autoritativa", instrucciones)
        self.assertIn("no ejecutes listar_archivos", instrucciones)
        self.assertEqual(herramientas_disponibles("control_puro"), HERRAMIENTAS)
        self.assertEqual(
            herramientas_disponibles("indice_autoritativo"),
            HERRAMIENTAS_SIN_LISTADO,
        )

    def test_selector_python_entrega_plan_compacto_sin_cargar_skill(self) -> None:
        """Separa la seleccion local de las instrucciones extensas de la Skill."""
        instrucciones = construir_instruccion_qwen("selector_python_compacto")
        solicitud = construir_solicitud_selector(
            {"archivos": [{"ruta": "backend/aplicacion.py"}]}
        )
        self.assertIn("Python ya selecciono el modo indice", instrucciones)
        self.assertNotIn("# Optimizar contexto", instrucciones)
        self.assertIn("PLAN_LOCAL_AUTORITATIVO", solicitud)
        self.assertIn("backend/aplicacion.py", solicitud)
        self.assertEqual(
            herramientas_disponibles("selector_python_compacto"), HERRAMIENTAS_SIN_LISTADO
        )

    def test_no_duplica_razonamiento_en_los_tokens_de_salida(self) -> None:
        """Mantiene salida facturable y desglose de razonamiento como campos distintos."""
        respuesta = SimpleNamespace(
            usage=SimpleNamespace(
                prompt_tokens=120,
                completion_tokens=45,
                completion_tokens_details=SimpleNamespace(reasoning_tokens=30),
            ),
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="Respuesta final", tool_calls=None),
                )
            ],
        )
        with tempfile.TemporaryDirectory(prefix="qwen-simulado-") as temporal:
            entorno = Path(temporal) / "aplicacion"
            shutil.copytree(FIXTURE, entorno)
            resultado = ejecutar_agente(
                ClienteFalso(respuesta),
                "qwen-simulado",
                "indice_autoritativo",
                entorno,
                {},
                True,
            )
        self.assertEqual(resultado["tokens_entrada"], 120)
        self.assertEqual(resultado["tokens_salida"], 45)
        self.assertEqual(resultado["tokens_razonamiento"], 30)

    def test_herramientas_eficientes_buscan_y_leen_lotes_acotados(self) -> None:
        """Entrega coincidencias y rangos breves en el contexto temporal generado."""
        with tempfile.TemporaryDirectory(prefix="qwen-eficiente-") as temporal:
            entorno = Path(temporal) / "aplicacion"
            shutil.copytree(FIXTURE, entorno)
            preparar_contexto_herramientas_eficientes(entorno)
            busqueda, truncadas_busqueda, lotes_busqueda = ejecutar_herramienta_eficiente(
                entorno,
                "buscar_texto",
                {"ruta": "backend/contrato_contexto.py", "texto": "MARCADOR_API"},
            )
            lote, truncadas_lote, lotes = ejecutar_herramienta_eficiente(
                entorno,
                "leer_lote",
                {
                    "lecturas": [
                        {"ruta": "backend/contrato_contexto.py", "inicio": 120, "limite": 8},
                        {"ruta": "interfaz/contrato_contexto.js", "inicio": 120, "limite": 8},
                    ]
                },
            )
        self.assertEqual(truncadas_busqueda, 0)
        self.assertEqual(lotes_busqueda, 0)
        self.assertEqual(busqueda["coincidencias"][0]["linea"], 124)
        self.assertEqual(truncadas_lote, 0)
        self.assertEqual(lotes, 1)
        self.assertEqual(len(lote["lecturas"]), 2)
        self.assertIn("MARCADOR_API", lote["lecturas"][0]["contenido"])
        self.assertIn("MARCADOR_INTERFAZ", lote["lecturas"][1]["contenido"])
        self.assertIn("buscar_texto", [herramienta["function"]["name"] for herramienta in HERRAMIENTAS_EFICIENTES])
        self.assertIn("leer_lote", [herramienta["function"]["name"] for herramienta in HERRAMIENTAS_EFICIENTES])
        self.assertIn("MARCADOR_API", solicitud_herramientas_eficientes())

    def test_cache_de_lectura_registra_acierto_y_rango_truncado(self) -> None:
        """Reutiliza una lectura identica y conserva el limite de lineas declarado."""
        llamada = SimpleNamespace(
            id="lectura-1",
            function=SimpleNamespace(
                name="leer_archivo",
                arguments='{"ruta":"backend/contrato_contexto.py","inicio":1,"limite":5}',
            ),
        )
        llamada_repetida = SimpleNamespace(
            id="lectura-2",
            function=SimpleNamespace(
                name="leer_archivo",
                arguments='{"ruta":"backend/contrato_contexto.py","inicio":1,"limite":5}',
            ),
        )
        def respuesta(solicitudes: list[object] | None) -> object:
            return SimpleNamespace(
                usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5, completion_tokens_details=None),
                choices=[SimpleNamespace(message=SimpleNamespace(content="final", tool_calls=solicitudes))],
            )
        with tempfile.TemporaryDirectory(prefix="qwen-cache-") as temporal:
            entorno = Path(temporal) / "aplicacion"
            shutil.copytree(FIXTURE, entorno)
            preparar_contexto_herramientas_eficientes(entorno)
            resultado = ejecutar_agente(
                ClienteFalso([respuesta([llamada]), respuesta([llamada_repetida]), respuesta(None)]),
                "qwen-simulado",
                "herramientas_eficientes",
                entorno,
                {},
                False,
            )
        self.assertEqual(resultado["aciertos_cache"], 1)
        self.assertEqual(resultado["lecturas_truncadas"], 1)
        self.assertTrue(resultado["mecanismos_activados"])


if __name__ == "__main__":
    unittest.main()
