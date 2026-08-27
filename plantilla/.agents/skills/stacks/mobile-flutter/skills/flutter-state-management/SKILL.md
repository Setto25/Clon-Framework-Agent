---
name: flutter-state-management
description: Guia para elegir e implementar state management en Flutter (BLoC, Riverpod, Provider). Incluye criterio de seleccion, patrones con TDD y testing. Usar cuando se defina la arquitectura de estado de una app Flutter o se implemente un nuevo Bloc/Notifier.
---

# Flutter State Management

## Cuando usar

- Definir la estrategia de estado de un proyecto Flutter nuevo.
- Implementar un Bloc, Notifier o Controller nuevo.
- Migrar de una solucion a otra.
- Decidir entre estado local vs compartido.

## Criterio de seleccion

### Constraints que evaluar

Antes de elegir, declarar:
1. Complejidad del estado (local simple vs logica de negocio compleja).
2. Requisitos de testabilidad (unit tests de logica independientes de UI).
3. Tamaño del equipo y experiencia previa.
4. Necesidad de reactividad (streams, real-time).

### Matriz de decision

| Solucion | Usar cuando | NO usar cuando |
|---|---|---|
| `setState` | Estado local de un solo widget, UI efimera | Logica compartida entre widgets |
| `Provider` | DI simple, apps pequeñas-medianas | Logica asincrona compleja, apps grandes |
| `Riverpod` | Apps modernas, seguridad en compilacion, auto-dispose | Equipo sin experiencia en Riverpod |
| `BLoC` | Logica compleja, testabilidad maxima, equipos grandes | Prototipos rapidos, estado trivial |
| `GetX` | Prototipos rapidos, minimo boilerplate | Apps en produccion con mantenimiento largo |

**Regla**: no mezclar multiples soluciones en un proyecto sin justificacion documentada.

## Patron 1: BLoC (recomendado para logica compleja)

### Test primero (red)

```dart
// test/bloc/bloc_pedidos_test.dart
import 'package:bloc_test/bloc_test.dart';

void main() {
  group('BlocPedidos', () {
    late RepositorioPedidos mockRepositorio;

    setUp(() {
      mockRepositorio = MockRepositorioPedidos();
    });

    blocTest<BlocPedidos, EstadoPedido>(
      'emite [Cargando, Cargado] al agregar CargarPedidos',
      build: () {
        when(() => mockRepositorio.obtenerPedidos())
            .thenAnswer((_) async => [Pedido(id: '1', total: 100)]);
        return BlocPedidos(repositorio: mockRepositorio);
      },
      act: (bloc) => bloc.add(CargarPedidos()),
      expect: () => [
        EstadoPedidoCargando(),
        isA<EstadoPedidoCargado>(),
      ],
    );

    blocTest<BlocPedidos, EstadoPedido>(
      'emite [Cargando, Error] cuando el repositorio falla',
      build: () {
        when(() => mockRepositorio.obtenerPedidos())
            .thenThrow(Exception('sin conexion'));
        return BlocPedidos(repositorio: mockRepositorio);
      },
      act: (bloc) => bloc.add(CargarPedidos()),
      expect: () => [
        EstadoPedidoCargando(),
        isA<EstadoPedidoError>(),
      ],
    );
  });
}
```

### Implementacion (green)

```dart
// Eventos
sealed class EventoPedido {}
class CargarPedidos extends EventoPedido {}
class RefrescarPedidos extends EventoPedido {}

// Estados
sealed class EstadoPedido {}
class EstadoPedidoInicial extends EstadoPedido {}
class EstadoPedidoCargando extends EstadoPedido {}

class EstadoPedidoCargado extends EstadoPedido {
  final List<Pedido> pedidos;
  EstadoPedidoCargado(this.pedidos);
}

class EstadoPedidoError extends EstadoPedido {
  final String mensaje;
  EstadoPedidoError(this.mensaje);
}

// Bloc
class BlocPedidos extends Bloc<EventoPedido, EstadoPedido> {
  final RepositorioPedidos repositorio;

  BlocPedidos({required this.repositorio}) : super(EstadoPedidoInicial()) {
    on<CargarPedidos>(_alCargar);
    on<RefrescarPedidos>(_alRefrescar);
  }

  Future<void> _alCargar(CargarPedidos evento, Emitter<EstadoPedido> emit) async {
    emit(EstadoPedidoCargando());
    try {
      final pedidos = await repositorio.obtenerPedidos();
      emit(EstadoPedidoCargado(pedidos));
    } catch (e) {
      emit(EstadoPedidoError(e.toString()));
    }
  }

  Future<void> _alRefrescar(RefrescarPedidos evento, Emitter<EstadoPedido> emit) async {
    try {
      final pedidos = await repositorio.obtenerPedidos();
      emit(EstadoPedidoCargado(pedidos));
    } catch (e) {
      emit(EstadoPedidoError(e.toString()));
    }
  }
}
```

### UI (consume el Bloc)

```dart
class PaginaPedidos extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => BlocPedidos(
        repositorio: context.read<RepositorioPedidos>(),
      )..add(CargarPedidos()),
      child: BlocBuilder<BlocPedidos, EstadoPedido>(
        builder: (context, estado) {
          return switch (estado) {
            EstadoPedidoInicial() => const SizedBox.shrink(),
            EstadoPedidoCargando() => const Center(child: CircularProgressIndicator()),
            EstadoPedidoCargado(pedidos: var pedidos) => ListView.builder(
              itemCount: pedidos.length,
              itemBuilder: (context, i) => TarjetaPedido(pedido: pedidos[i]),
            ),
            EstadoPedidoError(mensaje: var msg) => Center(child: Text('Error: $msg')),
          };
        },
      ),
    );
  }
}
```

## Patron 2: Riverpod (recomendado para apps modernas)

### Test primero (red)

```dart
void main() {
  test('notificadorUsuarios carga lista inicial', () async {
    final contenedor = ProviderContainer(overrides: [
      providerRepositorioUsuarios.overrideWithValue(MockRepositorioUsuarios()),
    ]);
    addTearDown(contenedor.dispose);

    await contenedor.read(providerListaUsuarios.future);
    final usuarios = contenedor.read(providerListaUsuarios).value;

    expect(usuarios, isNotEmpty);
    expect(usuarios!.first.nombre, 'Test');
  });
}
```

### Implementacion (green)

```dart
// Providers
final providerRepositorioUsuarios = Provider<RepositorioUsuarios>((ref) {
  return RepositorioUsuariosHttp();
});

final providerListaUsuarios =
    AsyncNotifierProvider<NotificadorUsuarios, List<Usuario>>(() {
  return NotificadorUsuarios();
});

// Notifier
class NotificadorUsuarios extends AsyncNotifier<List<Usuario>> {
  @override
  Future<List<Usuario>> build() async {
    final repo = ref.read(providerRepositorioUsuarios);
    return repo.obtenerUsuarios();
  }

  Future<void> refrescar() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final repo = ref.read(providerRepositorioUsuarios);
      return repo.obtenerUsuarios();
    });
  }
}

// UI
class PaginaUsuarios extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final usuariosAsync = ref.watch(providerListaUsuarios);

    return Scaffold(
      body: usuariosAsync.when(
        data: (usuarios) => ListView.builder(
          itemCount: usuarios.length,
          itemBuilder: (context, i) => ListTile(title: Text(usuarios[i].nombre)),
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text('Error: $error')),
      ),
    );
  }
}
```

## Patron 3: Provider (apps simples)

```dart
// Modelo con ChangeNotifier
class ModeloCarrito extends ChangeNotifier {
  final List<Producto> _items = [];
  List<Producto> get items => List.unmodifiable(_items);
  int get total => _items.fold(0, (sum, p) => sum + p.precio);

  void agregar(Producto producto) {
    _items.add(producto);
    notifyListeners();
  }

  void remover(Producto producto) {
    _items.remove(producto);
    notifyListeners();
  }
}

// Setup
void main() {
  runApp(
    ChangeNotifierProvider(create: (_) => ModeloCarrito(), child: MiApp()),
  );
}

// Consumir
class PaginaCarrito extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Consumer<ModeloCarrito>(
      builder: (context, carrito, child) {
        return Text('Total: \$${carrito.total}');
      },
    );
  }
}
```

## Reglas

- Elegir UNA solucion por proyecto y documentar la decision en PROJECT_STATE.md §4.
- Escribir el test del Bloc/Notifier ANTES de la implementacion.
- Los nombres de negocio de eventos, estados y blocs respetan el idioma declarado en `AGENTS.md`.
- Nombres del framework (`Bloc`, `Emitter`, `AsyncNotifier`, `ConsumerWidget`) en ingles.
- No poner logica de negocio en widgets — solo en Blocs/Notifiers/Controllers.
