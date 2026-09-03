# Modo extendido

Se aplica solo despues de una señal observable de escalamiento definida en `SKILL.md`.

## Protocolo

1. Registra de forma compacta el entregable, los hechos vigentes, las rutas ya consultadas y el siguiente bloqueo. No expongas este registro si la salida exige otro formato.
2. Si falta un mapa vigente, ejecuta `python scripts/generar_indice_contexto.py <terminos>` con un maximo de ocho terminos concretos. No regeneres el indice mientras la raiz, los terminos y los archivos relevantes no hayan cambiado.
3. Agrupa inspecciones independientes y selecciona como maximo 30 rutas pertinentes. Lee fragmentos o simbolos antes que archivos completos cuando sea suficiente.
4. Antes de repetir una consulta, comprueba si el registro o una salida anterior ya responde la pregunta. Si la evidencia sigue vigente, reutilizala.
5. Tras una validacion fallida, conserva solo el fallo, la hipotesis que se comprobara y las fuentes relacionadas. No reenvies salidas extensas sin necesidad.
6. Corrige el minimo alcance respaldado por el fallo y vuelve a ejecutar la validacion afectada.
7. Finaliza cuando los criterios solicitados aprueben. No agregues mejoras, inventarios ni verificaciones ajenas al alcance.

## Condiciones de salida

- La evidencia necesaria queda asociada a rutas o resultados observados.
- No quedan ciclos fallidos sin explicar.
- La validacion solicitada aprueba o el bloqueo comprobado queda informado.
- No se repiten consultas equivalentes ni se reconfirma el indice sin cambios.

El indice solo encuentra referencias literales. Las dependencias semanticas, el comportamiento en ejecucion y los efectos indirectos requieren razonamiento y pruebas dirigidas.
