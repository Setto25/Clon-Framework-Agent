# Modo arquitectonico

Se aplica despues del modo extendido cuando la tarea decide arquitectura, migra contratos o coordina varios sistemas.

## Revision adicional

1. Identifica limites de componentes, contratos publicos, propietarios de datos y dependencias en tiempo de ejecucion.
2. Separa hechos observados, inferencias y decisiones pendientes. Cada inferencia debe indicar la evidencia que la sostiene.
3. Comprueba impactos en compatibilidad, seguridad, datos, despliegue, reversibilidad, pruebas y documentacion.
4. Prioriza invariantes y decisiones sobre listados exhaustivos de archivos.
5. Para una migracion, define estado inicial, estado objetivo, pasos compatibles, validacion y mecanismo de recuperacion.
6. Lee implementacion adicional solo cuando resuelva una decision concreta o verifique un contrato.

## Salida

Entrega la decision, sus consecuencias y la evidencia minima suficiente. Si la tarea incluye implementacion, conserva ademas las condiciones de salida del modo extendido.
