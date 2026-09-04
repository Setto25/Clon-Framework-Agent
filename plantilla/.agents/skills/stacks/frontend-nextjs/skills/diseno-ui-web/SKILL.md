---
name: diseno-ui-web
description: Define o revisa interfaces web con una direccion visual propia, composicion contextual, accesibilidad y movimiento intencional; evita soluciones SaaS genericas y conserva sistemas visuales existentes.
---

# Diseno UI/UX web con identidad

Construye interfaces reconocibles por su producto y su dominio, no por una receta visual de moda. El impacto puede provenir de expresividad, precision o calma; nunca debe sacrificar comprension, rendimiento ni accesibilidad.

## Frontera de la Skill

- En un producto existente, conserva su lenguaje visual y sus patrones salvo que el usuario haya autorizado un rediseno.
- Respeta marca, referencias, contenido y restricciones confirmadas. No inventa una identidad incompatible para "hacerla moderna".
- No instala dependencias, tipografias remotas ni librerias de animacion sin comprobar el proyecto y el alcance autorizado.
- Usa tokens semanticos y componentes reutilizables, pero no confunde un sistema de diseno con una identidad visual.

## Direccion antes de componentes

Antes de escribir UI, identifica con la evidencia disponible:

1. quien usa la interfaz y que debe resolver;
2. cual es el objeto central del producto: conversacion, dispositivo, documento, escena, inventario, alerta u otro;
3. si la experiencia es principalmente operativa, transaccional, editorial, narrativa, inmersiva o intensiva en datos;
4. que sensacion debe producir y cual debe evitar;
5. que identidad, recursos y patrones ya existen.

Si una respuesta faltante cambia materialmente el resultado, consulta al usuario. Si no, declara una hipotesis reversible y continua. Para crear o cambiar una direccion visual, lee [referencias/direccion_visual.md](referencias/direccion_visual.md).

Define antes de implementar un breve concepto rector con:

- una idea visual vinculada al producto;
- una regla de composicion;
- una voz tipografica;
- una logica de color y material;
- un gesto distintivo que pueda recordarse sin depender del logotipo;
- limites explicitos para impedir exceso decorativo.

No presentes varias direcciones completas salvo que la tarea sea explorar alternativas. En implementacion, elige una y mantenla coherente.

## Composicion contextual

La arquitectura visual debe surgir del objeto y la tarea central. Una flota puede organizarse como territorio; una conversacion, como presencia y turnos; una investigacion, como evidencia y relaciones. No traduzcas automaticamente toda informacion a una cuadricula de tarjetas.

Evita como solucion predeterminada:

- encabezado, gran titulo, subtitulo y tres tarjetas intercambiables;
- mosaicos de metricas sin una decision asociada;
- panel lateral permanente cuando la jerarquia no lo necesita;
- degradados morado-azul, resplandores, vidrio y bordes luminosos usados solo para aparentar tecnologia;
- iconos dentro de circulos repetidos, textos de relleno y datos ficticios decorativos;
- tipografias, radios y sombras elegidos porque son habituales en plantillas.

Puede usar tarjetas, degradados o vidrio cuando expresen una jerarquia o materialidad concreta. La prohibicion es la repeticion sin razon, no la tecnica.

## Sistema visual

- Define tokens semanticos para fondo, superficie, texto, borde, acciones, estados y datos. Los valores pueden usar CSS moderno; evita colores utilitarios dispersos como contrato de producto.
- Selecciona tipografia por voz, legibilidad, idioma, licencia, privacidad y rendimiento. No limita la eleccion a una lista fija de fuentes populares.
- Usa escala, ritmo, espacio, alineacion y densidad para jerarquizar antes de agregar contenedores.
- Diferencia acciones primarias, riesgos, estados y contenido mediante mas de una senal; no depende solo del color.
- Disena estados reales: carga, vacio, error, desconexion, permiso insuficiente, exito y contenido extremo.
- Mantiene contraste, foco visible, navegacion por teclado, objetivos tactiles adecuados y HTML semantico.
- Soporta temas solo si el producto lo requiere o ya los ofrece. Un modo oscuro no constituye por si mismo una direccion visual.

## Movimiento con proposito

Usa movimiento para explicar causalidad, mantener continuidad, orientar la atencion o dar respuesta a una accion. Si el desplazamiento debe producir un recorrido visual, una revelacion espacial o una secuencia narrativa, lee [referencias/movimiento_narrativo.md](referencias/movimiento_narrativo.md).

- No bloquea ni secuestra el scroll nativo.
- Respeta `prefers-reduced-motion` y ofrece una version comprensible sin animacion.
- Evita animar todas las superficies o usar paralaje como decoracion repetida.
- Reserva bibliotecas de animacion, canvas o WebGL para efectos que CSS y la plataforma no resuelvan con suficiente calidad.
- En vistas operativas, prioriza respuesta inmediata, estabilidad espacial y baja carga cognitiva.

## Implementacion y comprobacion

1. Audita primero estilos, componentes y dependencias existentes.
2. Registra el concepto rector y traduce sus reglas a tokens, layout y componentes.
3. Implementa una seccion representativa antes de propagar el sistema completo.
4. Verifica comportamiento responsivo, teclado, contraste, reduccion de movimiento, datos largos y estados adversos.
5. Revisa la interfaz sin logotipo ni texto promocional. Si podria pertenecer sin cambios a cualquier producto, redefine al menos composicion, voz visual o gesto distintivo.
6. Comprueba que el impacto refuerce la tarea principal. Si compite con ella, reduce el efecto.

Una interfaz no se considera diferenciada por acumular efectos. Debe expresar una idea coherente, apropiada al dominio y reconocible en sus decisiones estructurales.
