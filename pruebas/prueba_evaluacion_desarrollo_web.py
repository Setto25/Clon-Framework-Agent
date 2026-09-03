#!/usr/bin/env python3
"""Comprueba el escenario web aislado sin consumir una API de modelos."""

from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path


DEPENDENCIAS_DISPONIBLES = all(
    importlib.util.find_spec(modulo) is not None
    for modulo in ("fastapi", "httpx", "google.genai")
) and shutil.which("node") is not None

if DEPENDENCIAS_DISPONIBLES:
    from scripts.evaluar_desarrollo_web_gemini import (
        FIXTURE,
        VARIANTES,
        construir_instruccion,
        construir_solicitud,
        ejecutar_validacion,
        escribir_archivo,
        requiere_correccion_cierre,
    )


@unittest.skipUnless(
    DEPENDENCIAS_DISPONIBLES,
    "El escenario opcional requiere FastAPI, httpx, google-genai y Node.js",
)
class PruebasEvaluacionDesarrolloWeb(unittest.TestCase):
    """Valida aislamiento, fallos iniciales y posibilidad real de solucion."""

    def setUp(self) -> None:
        """Copia el fixture a un directorio temporal independiente."""
        self.temporal = tempfile.TemporaryDirectory(prefix="evaluacion-web-")
        self.entorno = Path(self.temporal.name) / "aplicacion"
        shutil.copytree(FIXTURE, self.entorno)

    def tearDown(self) -> None:
        """Elimina exclusivamente la copia temporal creada por el caso."""
        self.temporal.cleanup()

    def test_fixture_inicial_exige_implementacion(self) -> None:
        """Confirma que el punto de partida no aprueba por accidente."""
        resultado = ejecutar_validacion(self.entorno)
        self.assertFalse(resultado["aprobada"])

    def test_reabre_un_cierre_con_pruebas_fallidas(self) -> None:
        """Impide que una respuesta textual cierre cuando la validacion aun falla."""
        resultado = ejecutar_validacion(self.entorno)
        self.assertTrue(requiere_correccion_cierre(resultado, 0))
        self.assertFalse(requiere_correccion_cierre(resultado, 2))

    def test_impide_modificar_las_pruebas(self) -> None:
        """Mantiene la evidencia de eficacia fuera del alcance del agente."""
        resultado = escribir_archivo(
            self.entorno,
            "pruebas/prueba_backend.py",
            "# intento no autorizado\n",
        )
        self.assertIn("error", resultado)

    def test_distingue_seleccion_y_protocolo_compacto(self) -> None:
        """Conserva tratamientos que permiten atribuir cada diferencia observada."""
        self.assertEqual(
            VARIANTES,
            (
                "control_puro",
                "indice",
                "skill_adaptativa",
                "skill_extendida",
                "extendido_compacto",
            ),
        )
        adaptativa = construir_instruccion("skill_adaptativa")
        extendida = construir_instruccion("skill_extendida")
        compacta = construir_instruccion("extendido_compacto")
        self.assertIn("Selecciona y aplica el modo menos costoso", adaptativa)
        self.assertNotIn("# Modo extendido", adaptativa)
        self.assertIn("Usa obligatoriamente el modo extendido", extendida)
        self.assertIn("# Modo extendido", extendida)
        self.assertNotIn("# Optimizar contexto", compacta)
        self.assertIn("# Modo extendido", compacta)
        self.assertNotIn("# Modo arquitectonico", compacta)
        self.assertNotIn("INDICE_LOCAL_INICIAL", construir_solicitud("control_puro", {}))
        self.assertIn("INDICE_LOCAL_INICIAL", construir_solicitud("skill_extendida", {}))

    def test_fixture_admite_una_solucion_completa(self) -> None:
        """Demuestra que los requisitos pueden satisfacerse dentro del presupuesto."""
        backend = '''"""Expone operaciones completas para el tablero de tareas."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from backend.modelos import TAREAS, Tarea


class EntradaTarea(BaseModel):
    """Valida el contrato de creacion recibido por la API."""

    titulo: str


aplicacion = FastAPI(title="Tablero de tareas")


@aplicacion.get("/api/tareas")
def listar_tareas() -> list[Tarea]:
    """Devuelve las tareas existentes."""
    return TAREAS


@aplicacion.post("/api/tareas", status_code=status.HTTP_201_CREATED)
def crear_tarea(entrada: EntradaTarea) -> Tarea:
    """Crea una tarea con titulo normalizado e id incremental."""
    titulo = entrada.titulo.strip()
    if not titulo:
        raise HTTPException(status_code=422, detail="El titulo es obligatorio")
    tarea: Tarea = {
        "id": max((tarea["id"] for tarea in TAREAS), default=0) + 1,
        "titulo": titulo,
        "completada": False,
    }
    TAREAS.append(tarea)
    return tarea


@aplicacion.patch("/api/tareas/{identificador}")
def alternar_tarea(identificador: int) -> Tarea:
    """Alterna una tarea existente o informa que no existe."""
    tarea = next((tarea for tarea in TAREAS if tarea["id"] == identificador), None)
    if tarea is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    tarea["completada"] = not tarea["completada"]
    return tarea
'''
        html = '''<!doctype html>
<html lang="es">
  <body>
    <main>
      <h1>Tablero de tareas</h1>
      <form id="formulario-tarea">
        <label for="titulo-tarea">Nueva tarea</label>
        <input id="titulo-tarea" required>
        <button type="submit">Agregar</button>
      </form>
      <nav aria-label="Filtros">
        <button data-filtro="todas">Todas</button>
        <button data-filtro="pendientes">Pendientes</button>
        <button data-filtro="completadas">Completadas</button>
      </nav>
      <p id="estado" aria-live="polite"></p>
      <ul id="lista-tareas"></ul>
    </main>
    <script type="module" src="aplicacion.js"></script>
  </body>
</html>
'''
        javascript = '''const formulario = document.querySelector("#formulario-tarea");
const entrada = document.querySelector("#titulo-tarea");
const lista = document.querySelector("#lista-tareas");
const estado = document.querySelector("#estado");
let tareas = [];
let filtro = "todas";

function visibles() {
  if (filtro === "pendientes") return tareas.filter((tarea) => !tarea.completada);
  if (filtro === "completadas") return tareas.filter((tarea) => tarea.completada);
  return tareas;
}

function renderizar() {
  lista.replaceChildren(...visibles().map((tarea) => {
    const elemento = document.createElement("li");
    const boton = document.createElement("button");
    boton.textContent = tarea.titulo;
    boton.addEventListener("click", async () => {
      const respuesta = await fetch(`/api/tareas/${tarea.id}`, { method: "PATCH" });
      Object.assign(tarea, await respuesta.json());
      renderizar();
    });
    elemento.append(boton);
    return elemento;
  }));
}

formulario.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const respuesta = await fetch("/api/tareas", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ titulo: entrada.value }),
  });
  if (respuesta.ok) tareas.push(await respuesta.json());
  estado.textContent = respuesta.ok ? "Tarea agregada" : "No se pudo agregar";
  renderizar();
});

document.querySelectorAll("[data-filtro]").forEach((boton) => {
  boton.addEventListener("click", () => {
    filtro = boton.dataset.filtro;
    renderizar();
  });
});
'''
        self.assertNotIn(
            "error",
            escribir_archivo(self.entorno, "backend/aplicacion.py", backend),
        )
        self.assertNotIn(
            "error",
            escribir_archivo(self.entorno, "interfaz/interfaz.html", html),
        )
        self.assertNotIn(
            "error",
            escribir_archivo(self.entorno, "interfaz/aplicacion.js", javascript),
        )
        resultado = ejecutar_validacion(self.entorno)
        self.assertTrue(resultado["aprobada"], resultado)


if __name__ == "__main__":
    unittest.main()
