---
name: flutter-performance
description: Optimizacion de rendimiento en Flutter. Cubre rebuilds innecesarios, listas eficientes, imagenes, memoria, isolates y profiling con DevTools. Usar cuando la app presenta jank, uso excesivo de memoria, o antes de release para auditar rendimiento.
---

# Flutter Performance

## Cuando usar

- La app presenta frames perdidos o lag visible.
- Uso de memoria crece sin control.
- Scroll de listas largas no es fluido.
- Antes de release: auditoria de rendimiento.
- Al agregar animaciones costosas.

## Principio general

Medir ANTES de optimizar. Usar DevTools para identificar el cuello de botella real:

```bash
flutter run --profile
# En otra terminal:
dart devtools
```

## 1. Rebuilds de widgets

### Problema: widgets que se reconstruyen sin necesidad

```dart
// MAL: todo se reconstruye al cambiar _contador
class Ejemplo extends StatefulWidget { ... }
class _EstadoEjemplo extends State<Ejemplo> {
  int _contador = 0;

  @override
  Widget build(BuildContext context) {
    return Column(children: [
      WidgetCostoso(),           // se reconstruye innecesariamente
      Text('$_contador'),
    ]);
  }
}

// BIEN: extraer widget costoso como const
class _EstadoEjemplo extends State<Ejemplo> {
  int _contador = 0;

  @override
  Widget build(BuildContext context) {
    return Column(children: [
      const WidgetCostoso(),    // const = no se reconstruye
      Text('$_contador'),
    ]);
  }
}
```

### Regla: usar `const` en todo widget que no dependa de estado mutable.

## 2. Listas eficientes

```dart
// MAL: construye TODOS los items de golpe
ListView(
  children: items.map((item) => TarjetaItem(item: item)).toList(),
)

// BIEN: construye solo los visibles
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, i) => TarjetaItem(item: items[i]),
)
```

Para listas con separadores:
```dart
ListView.separated(
  itemCount: items.length,
  separatorBuilder: (_, __) => const Divider(),
  itemBuilder: (context, i) => TarjetaItem(item: items[i]),
)
```

## 3. Imagenes

```dart
// Redimensionar en memoria (no cargar imagen 4K para un thumbnail)
Image.network(
  url,
  cacheWidth: 300,
  cacheHeight: 300,
)

// Precarga de imagenes criticas
@override
void didChangeDependencies() {
  super.didChangeDependencies();
  precacheImage(const AssetImage('assets/fondo.png'), context);
}
```

Paquete recomendado: `cached_network_image` para cache automatico con placeholder.

## 4. Memoria

```dart
// SIEMPRE dispose de controllers y subscriptions
class _EstadoPagina extends State<PaginaScroll> {
  late ScrollController _controlador;
  late StreamSubscription _subscripcion;

  @override
  void initState() {
    super.initState();
    _controlador = ScrollController();
    _subscripcion = streamDatos.listen((datos) { /* ... */ });
  }

  @override
  void dispose() {
    _controlador.dispose();
    _subscripcion.cancel();
    super.dispose();
  }
}
```

## 5. Aislamiento de repintado

```dart
// Aislar widgets con animaciones costosas del arbol padre
RepaintBoundary(
  child: WidgetAnimado(),
)

// Util tambien para CustomPaint complejos
RepaintBoundary(
  child: CustomPaint(painter: PintorComplejo()),
)
```

## 6. Computo pesado en isolates

```dart
// Mover parsing/procesamiento pesado fuera del main isolate
Future<List<Producto>> cargarProductos(String json) async {
  return Isolate.run(() {
    final parsed = jsonDecode(json) as List;
    return parsed.map((e) => Producto.fromJson(e)).toList();
  });
}

// Para operaciones mas simples: compute()
final resultado = await compute(parsearJson, respuesta.body);
```

## Checklist pre-release

- [ ] `flutter run --profile` sin frames rojos en el performance overlay
- [ ] Listas largas usan `ListView.builder`
- [ ] No hay `setState` que reconstruya arboles grandes
- [ ] Imagenes redimensionadas al tamaño de display
- [ ] Controllers y subscriptions tienen `dispose()`
- [ ] Widgets estaticos marcados como `const`
- [ ] Animaciones costosas envueltas en `RepaintBoundary`
- [ ] Computo pesado en `Isolate.run` o `compute`

## Reglas

- No optimizar sin medir. DevTools primero.
- Un rebuild innecesario en un frame no es problema. Miles por segundo si lo son.
- `const` es gratis — usarlo siempre que sea posible.
- Preferir soluciones del framework (`ListView.builder`, `RepaintBoundary`) antes que trucos custom.
