"""Define el dominio independiente del protocolo y del transporte."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ErrorAutorizacion(Exception):
    """Representa una operacion fuera de la autoridad de una identidad."""


class ErrorEntrada(Exception):
    """Representa argumentos que no cumplen el contrato del dominio."""


class ErrorConflictoIdempotencia(Exception):
    """Representa la reutilizacion incompatible de una clave idempotente."""


@dataclass(frozen=True)
class Identidad:
    """Representa una identidad autenticada con alcances normalizados."""

    sujeto: str
    alcances: frozenset[str]


@dataclass(frozen=True)
class EstadoContador:
    """Representa el valor observable de un contador."""

    contador_id: str
    valor: int
    operacion_id: str | None = None
    repetida: bool = False


class AlmacenContadores(Protocol):
    """Define la persistencia requerida por el servicio de contadores."""

    def consultar(self, contador_id: str) -> EstadoContador:
        """Devuelve el estado actual de un contador."""

    def incrementar(
        self,
        contador_id: str,
        cantidad: int,
        clave_idempotencia: str,
    ) -> EstadoContador:
        """Incrementa una vez y devuelve el mismo resultado ante un reintento."""


class AlmacenContadoresMemoria:
    """Mantiene un almacenamiento reemplazable para el piloto local."""

    def __init__(self) -> None:
        """Inicializa contadores y operaciones idempotentes vacios."""
        self._valores: dict[str, int] = {}
        self._operaciones: dict[str, tuple[str, int, EstadoContador]] = {}

    def consultar(self, contador_id: str) -> EstadoContador:
        """Devuelve cero cuando el contador aun no existe."""
        return EstadoContador(contador_id=contador_id, valor=self._valores.get(contador_id, 0))

    def incrementar(
        self,
        contador_id: str,
        cantidad: int,
        clave_idempotencia: str,
    ) -> EstadoContador:
        """Conserva la primera respuesta asociada a una clave idempotente."""
        anterior = self._operaciones.get(clave_idempotencia)
        if anterior is not None:
            contador_anterior, cantidad_anterior, resultado_anterior = anterior
            if contador_anterior != contador_id or cantidad_anterior != cantidad:
                raise ErrorConflictoIdempotencia(
                    "La clave de idempotencia ya fue usada con otros argumentos"
                )
            return EstadoContador(
                contador_id=resultado_anterior.contador_id,
                valor=resultado_anterior.valor,
                operacion_id=resultado_anterior.operacion_id,
                repetida=True,
            )

        valor = self._valores.get(contador_id, 0) + cantidad
        self._valores[contador_id] = valor
        resultado = EstadoContador(
            contador_id=contador_id,
            valor=valor,
            operacion_id=clave_idempotencia,
        )
        self._operaciones[clave_idempotencia] = (contador_id, cantidad, resultado)
        return resultado


class AutorizadorContadores:
    """Aplica alcances por operacion fuera del modelo y del protocolo."""

    def exigir(self, identidad: Identidad | None, alcance: str) -> Identidad:
        """Devuelve la identidad cuando posee el alcance requerido."""
        if identidad is None or alcance not in identidad.alcances:
            raise ErrorAutorizacion("La identidad no posee el alcance requerido")
        return identidad


class ServicioContadores:
    """Orquesta consultas e incrementos sin depender de MCP ni HTTP."""

    def __init__(self, almacen: AlmacenContadores, autorizador: AutorizadorContadores) -> None:
        """Recibe puertos reemplazables de persistencia y autorizacion."""
        self._almacen = almacen
        self._autorizador = autorizador

    def consultar(self, contador_id: str, identidad: Identidad | None) -> EstadoContador:
        """Consulta un contador despues de comprobar su autoridad."""
        self._validar_contador(contador_id)
        self._autorizador.exigir(identidad, "contadores:leer")
        return self._almacen.consultar(contador_id)

    def incrementar(
        self,
        contador_id: str,
        cantidad: int,
        clave_idempotencia: str,
        identidad: Identidad | None,
    ) -> EstadoContador:
        """Incrementa un contador una sola vez despues de autorizar la mutacion."""
        self._validar_contador(contador_id)
        if cantidad < 1 or cantidad > 100:
            raise ErrorEntrada("La cantidad debe estar entre 1 y 100")
        if not clave_idempotencia.strip() or len(clave_idempotencia) > 128:
            raise ErrorEntrada("La clave de idempotencia debe contener entre 1 y 128 caracteres")
        identidad_confirmada = self._autorizador.exigir(identidad, "contadores:escribir")
        clave_acotada = f"{identidad_confirmada.sujeto}:{clave_idempotencia}"
        resultado = self._almacen.incrementar(contador_id, cantidad, clave_acotada)
        return EstadoContador(
            contador_id=resultado.contador_id,
            valor=resultado.valor,
            operacion_id=clave_idempotencia,
            repetida=resultado.repetida,
        )

    @staticmethod
    def _validar_contador(contador_id: str) -> None:
        """Rechaza identificadores vacios o excesivos."""
        if not contador_id.strip() or len(contador_id) > 64:
            raise ErrorEntrada("El identificador debe contener entre 1 y 64 caracteres")
