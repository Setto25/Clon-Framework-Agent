"""Define el almacenamiento minimo de tareas del fixture."""

from __future__ import annotations

from typing import TypedDict


class Tarea(TypedDict):
    """Representa una tarea serializable por la API."""

    id: int
    titulo: str
    completada: bool


TAREAS: list[Tarea] = [
    {"id": 1, "titulo": "Revisar inventario", "completada": False},
    {"id": 2, "titulo": "Publicar informe", "completada": True},
]
