# Guia de operacion — {{NOMBRE_PROYECTO}}

## Estado inicial

{{ESTADO_BREVE}}

## Infraestructura confirmada

{{HARDWARE_O_INFRA}}

## Ejecucion local

<!-- TODO: Documenta el comando de ejecucion cuando exista el primer componente ejecutable. -->

## Verificacion

<!-- TODO: Documenta las pruebas y comprobaciones operativas del primer modulo. -->

Se crea `contrato_validacion.json` desde `contrato_validacion.ejemplo.json` y se ajustan sus modulos, directorios, comandos, timeouts y documentos. La prevalidacion reproducible se ejecuta con:

```powershell
python scripts/validar_cierre_tarea.py . --solo-verificaciones --salida-evidencia documentacion/EVIDENCIA_CIERRE.json
```

Solo un codigo cero habilita declarar el modulo terminado.

La comprobacion estatica independiente se ejecuta con `python scripts/validar_integridad_proyecto.py .`. En GitHub, `.github/workflows/validacion-proyecto.yml` la ejecuta en cada push y pull request con la revision base para exigir cambios simultaneos en estado, plan y registro. Esta puerta no instala dependencias ni reemplaza la prevalidacion ejecutable. Si falla `lint` o `build`, se repara el comando o la implementacion sin retirar la verificacion.

## Diagnostico

1. Reproduce el fallo con una entrada conocida.
2. Registra el error exacto y el componente afectado.
3. Aisla la capa responsable antes de cambiar codigo.
4. Verifica la correccion con la prueba que reproducia el fallo.
5. Ejecuta `python scripts/diagnosticar_tarea.py . --formato json` desde la raiz para incluir modulos anidados y revisar estados distintos de `APROBADO`.

## Bloqueos conocidos

{{BLOQUEOS}}
