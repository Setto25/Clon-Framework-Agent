"""Expone la aplicacion ASGI configurada desde el entorno."""

from codigo_servidor.aplicacion_http import crear_aplicacion
from codigo_servidor.configuracion import ConfiguracionServidor


aplicacion = crear_aplicacion(ConfiguracionServidor.desde_entorno())
