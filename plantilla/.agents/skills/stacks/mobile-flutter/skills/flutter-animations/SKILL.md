---
name: flutter-animations
description: Guia de animaciones en Flutter. Cubre implicitas (AnimatedContainer), explicitas (AnimationController), hero transitions, staggered y physics-based. Usar cuando se necesite agregar transiciones, movimiento o feedback visual a la UI.
---

# Flutter Animations

## Cuando usar

- Agregar transiciones entre estados de UI.
- Implementar feedback visual (tap, hover, loading).
- Crear hero animations entre pantallas.
- Animaciones secuenciales (staggered).
- Movimiento basado en fisica (spring, drag).

## Criterio de seleccion

| Tipo | Usar cuando | Complejidad |
|---|---|---|
| Implicita (`AnimatedX`) | Cambio simple de propiedad (tamaño, color, posicion) | Baja |
| `TweenAnimationBuilder` | Animacion custom sin controller | Baja-media |
| Explicita (`AnimationController`) | Control total: play, pause, reverse, repeat | Media |
| Hero | Transicion de un elemento entre pantallas | Baja |
| Staggered | Secuencia de animaciones coordinadas | Alta |
| Physics-based | Movimiento natural (spring, fling, gravity) | Media-alta |

**Regla**: empezar siempre por la opcion mas simple. Si `AnimatedContainer` resuelve el caso, no usar `AnimationController`.

## 1. Implicitas (preferir para casos simples)

```dart
class TarjetaExpandible extends StatefulWidget {
  @override
  State<TarjetaExpandible> createState() => _EstadoTarjetaExpandible();
}

class _EstadoTarjetaExpandible extends State<TarjetaExpandible> {
  bool _expandida = false;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => setState(() => _expandida = !_expandida),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
        width: _expandida ? 200 : 100,
        height: _expandida ? 200 : 100,
        decoration: BoxDecoration(
          color: _expandida ? Colors.blue : Colors.grey,
          borderRadius: BorderRadius.circular(_expandida ? 16 : 8),
        ),
      ),
    );
  }
}
```

Otros widgets implicitos utiles: `AnimatedOpacity`, `AnimatedAlign`, `AnimatedPadding`, `AnimatedSwitcher`.

## 2. Explicitas (control total)

### Test primero

```dart
void main() {
  testWidgets('WidgetFadeIn se vuelve visible', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: WidgetFadeIn(child: Text('hola'))));

    // Inicialmente invisible
    expect(find.text('hola'), findsOneWidget);
    final opacidad = tester.widget<FadeTransition>(find.byType(FadeTransition));
    expect(opacidad.opacity.value, 0.0);

    // Despues de la animacion
    await tester.pumpAndSettle();
    expect(opacidad.opacity.value, 1.0);
  });
}
```

### Implementacion

```dart
class WidgetFadeIn extends StatefulWidget {
  final Widget child;
  final Duration duracion;

  const WidgetFadeIn({
    required this.child,
    this.duracion = const Duration(milliseconds: 500),
  });

  @override
  State<WidgetFadeIn> createState() => _EstadoWidgetFadeIn();
}

class _EstadoWidgetFadeIn extends State<WidgetFadeIn>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animacion;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(duration: widget.duracion, vsync: this);
    _animacion = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeIn),
    );
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(opacity: _animacion, child: widget.child);
  }
}
```

## 3. Hero (entre pantallas)

```dart
// Pantalla origen
GestureDetector(
  onTap: () => Navigator.push(context, MaterialPageRoute(
    builder: (_) => PantallaDetalle(producto: producto),
  )),
  child: Hero(
    tag: 'producto-${producto.id}',
    child: ImagenProducto(url: producto.imagenUrl),
  ),
)

// Pantalla destino
class PantallaDetalle extends StatelessWidget {
  final Producto producto;
  const PantallaDetalle({required this.producto});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Hero(
        tag: 'producto-${producto.id}',
        child: ImagenProducto(url: producto.imagenUrl, tamano: 300),
      ),
    );
  }
}
```

**Regla**: el `tag` debe ser unico por instancia. Usar el id del modelo.

## 4. Staggered (secuenciales)

```dart
class AnimacionEscalonada extends StatefulWidget { ... }

class _Estado extends State<AnimacionEscalonada>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _opacidad;
  late Animation<double> _escala;
  late Animation<Offset> _posicion;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    );

    // Cada animacion ocupa un intervalo diferente
    _opacidad = Tween(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: const Interval(0.0, 0.3)),
    );
    _escala = Tween(begin: 0.5, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: const Interval(0.3, 0.6)),
    );
    _posicion = Tween(begin: const Offset(0, 50), end: Offset.zero).animate(
      CurvedAnimation(parent: _controller, curve: const Interval(0.6, 1.0)),
    );

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Opacity(
          opacity: _opacidad.value,
          child: Transform.scale(
            scale: _escala.value,
            child: Transform.translate(offset: _posicion.value, child: child),
          ),
        );
      },
      child: const WidgetContenido(),
    );
  }
}
```

## 5. Physics-based (spring)

```dart
class AnimacionSpring extends StatefulWidget { ... }

class _Estado extends State<AnimacionSpring>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(vsync: this, upperBound: 300);
  }

  void _ejecutar() {
    _controller.animateWith(
      SpringSimulation(
        const SpringDescription(mass: 1, stiffness: 100, damping: 10),
        _controller.value, // posicion actual
        300,               // destino
        0,                 // velocidad inicial
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: _ejecutar,
      child: AnimatedBuilder(
        animation: _controller,
        builder: (_, child) => Transform.translate(
          offset: Offset(0, _controller.value),
          child: child,
        ),
        child: const Circulo(),
      ),
    );
  }
}
```

## Reglas

- Empezar por la animacion implicita mas simple. Escalar a explicita solo si se necesita control.
- SIEMPRE `dispose()` el `AnimationController`.
- Usar `AnimatedBuilder` en vez de `setState` en el listener — mejor rendimiento.
- Envolver animaciones costosas en `RepaintBoundary`.
- Usar `const` en el `child` de `AnimatedBuilder` para evitar rebuilds.
- Probar animaciones en dispositivos reales — el emulador no refleja rendimiento real.
- Los nombres de clases de negocio respetan el idioma declarado en `AGENTS.md`.
