# Movimiento narrativo y scrollytelling

Se consulta cuando el desplazamiento deba revelar una historia, un proceso, una relacion espacial o una transformacion. No se usa para decorar formularios, tablas o controles frecuentes.

## Cuando aporta valor

Resulta adecuado si el contenido tiene una secuencia real, por ejemplo:

- explicar como un dispositivo percibe, decide y actua;
- viajar desde una vista de flota hasta el interior de un equipo;
- recorrer una linea temporal, un sistema fisico o capas de evidencia;
- presentar un producto cuya comprension depende de cambios de escala o contexto.

En un panel operativo continuo, usa animaciones locales y conserva posiciones estables. La experiencia narrativa puede vivir en la presentacion, el onboarding o una explicacion separada.

## Guion antes de animacion

Define escenas con cuatro datos:

1. que debe comprender la persona;
2. que permanece anclado para conservar contexto;
3. que cambia con el progreso;
4. que contenido y accion quedan disponibles sin animacion.

Cada escena debe aportar informacion nueva. Si dos tramos solo cambian el fondo o desplazan particulas, combinalos o eliminalos.

## Patrones seguros

- Usa una seccion `sticky` con progreso limitado cuando un objeto central deba mantenerse visible.
- Vincula opacidad, escala o posicion a intervalos acotados; evita movimientos permanentes sin reposo visual.
- Mantiene el texto en el flujo del documento para lectura, seleccion, tecnologias de asistencia y busqueda.
- Prefiere CSS, `IntersectionObserver` y animaciones compuestas por transformaciones u opacidad para recorridos simples.
- Incorpora una libreria, canvas o WebGL solo cuando exista una necesidad visual concreta y se pueda medir su coste.
- Permite navegar directamente a contenido y acciones; el scroll no debe ser la unica interfaz.

## Accesibilidad, dispositivos y rendimiento

- Con `prefers-reduced-motion: reduce`, elimina paralaje, interpolaciones continuas y desplazamientos amplios; conserva estados finales y orden narrativo.
- No altera la velocidad, inercia ni direccion del scroll del navegador.
- Evita cambios de layout durante el recorrido y reserva espacio para medios.
- Limita trabajo por cuadro, prueba equipos modestos y no vincula lecturas costosas del layout a cada evento de scroll.
- Disena una composicion movil propia cuando la escena horizontal o multicapa no quepa; no se limita a encogerla.
- Pausa medios fuera de pantalla y no obliga a descargar recursos pesados antes de mostrar contenido esencial.

## Criterio de aceptacion

El recorrido debe seguir siendo comprensible con movimiento reducido, teclado, pantalla estrecha y carga incompleta. La animacion se conserva solo si mejora orientacion, causalidad o recuerdo sin retrasar la accion principal.
