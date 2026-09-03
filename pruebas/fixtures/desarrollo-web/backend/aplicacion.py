"""Expone la API inicial de tareas que el agente debe completar."""

from __future__ import annotations

from fastapi import FastAPI

from backend.modelos import TAREAS, Tarea


aplicacion = FastAPI(title="Tablero de tareas")


@aplicacion.get("/api/tareas")
def listar_tareas() -> list[Tarea]:
    """Devuelve las tareas existentes sin modificar el almacenamiento."""
    return TAREAS
