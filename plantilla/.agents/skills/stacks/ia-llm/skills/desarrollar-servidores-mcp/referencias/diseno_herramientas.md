# Diseño de capacidades MCP

## Contrato antes del codigo

Para cada capacidad registrar:

- nombre estable y proposito observable;
- entrada tipada, limites y valores predeterminados;
- salida estructurada y representacion textual si mejora compatibilidad;
- errores de dominio distinguibles de fallos internos;
- autoridad necesaria, efectos laterales e idempotencia;
- timeout, tamaño maximo y estrategia de paginacion;
- ejemplos validos y casos rechazados.

El nombre describe una accion concreta. Evitar tools generales como `ejecutar`, argumentos libres que el servidor reinterpreta y esquemas que aceptan propiedades desconocidas sin necesidad.

## Tool, resource o prompt

Una tool ejecuta una accion o consulta parametrizada. Un resource representa contenido con identidad y puede permitir descubrimiento. Un prompt ofrece una plantilla seleccionada por el usuario. La eleccion debe reflejar la semantica, no la comodidad de una decoracion del SDK.

Las anotaciones sobre lectura, destruccion o idempotencia ayudan al cliente a presentar la capacidad, pero no se consideran controles confiables. El servidor vuelve a comprobar identidad, autoridad y argumentos en cada ejecucion.

## Entradas y salidas

- Usar esquemas cerrados y tipos precisos.
- Separar identificadores opacos de texto visible.
- Expresar unidades, zonas horarias, formatos y limites.
- Devolver solo los campos necesarios para la siguiente decision.
- Paginar colecciones potencialmente grandes.
- Evitar filtrar trazas, secretos o detalles internos en errores.
- Incluir un identificador de correlacion cuando ayude a soporte sin revelar datos sensibles.

Para operaciones mutables, aceptar una clave de idempotencia cuando puedan repetirse por red. Una validacion previa no sustituye la aprobacion de la accion real: vincular la aprobacion a identidad, argumentos normalizados, vencimiento y operacion.

## Errores

Clasificar al menos:

- entrada invalida;
- no autenticado;
- no autorizado;
- recurso inexistente o conflicto;
- dependencia temporalmente indisponible;
- limite de uso;
- fallo interno no revelado.

Los errores previsibles se prueban como parte del contrato. Los fallos internos conservan detalle en telemetria protegida y entregan al cliente un mensaje seguro y accionable.

## Evolucion

Mantener fixtures de solicitudes y respuestas publicadas. Un cambio compatible agrega informacion opcional o una capacidad nueva. Renombrar, eliminar, ampliar efectos laterales o endurecer un campo requerido exige migracion y prueba con clientes existentes.

## Revision minima

Antes de publicar una capacidad, comprobar que un cliente puede descubrirla, comprender el esquema, invocarla con un caso valido, recibir un rechazo estable para un caso invalido y distinguir un error transitorio sin depender de texto libre.
