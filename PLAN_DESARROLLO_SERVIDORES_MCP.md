# Plan de desarrollo: Skill para servidores MCP remotos

**Estado:** en implementacion; Hitos 0 a 3 completados localmente, piloto pendiente

**Linea base:** `3a58064`

**Fecha:** 2026-09-03

**Skill objetivo:** `desarrollar-servidores-mcp`

**Ubicacion prevista:** `plantilla/.agents/skills/stacks/ia-llm/skills/desarrollar-servidores-mcp/`

**Progreso al 2026-09-03:** la revision vigente del protocolo se fijo en MCP 2026-07-28; la Skill canonica, sus cinco referencias, catalogo, atribuciones, inventario y regresiones deterministas ya fueron incorporados. El SDK se fijara junto con el fixture del Hito 4 para no introducir una dependencia sin un piloto ejecutable. No se ha creado ni desplegado ningun recurso cloud.

## 1. Proposito

Este plan define como incorporar al framework una Skill que permita a cualquier agente compatible diseñar, implementar, probar, desplegar y mantener servidores MCP propios. El resultado debe ser agnostico del agente, remoto desde el inicio y portable entre proveedores de infraestructura.

El caso inicial es deliberadamente pequeño: una persona desarrolla un servidor MCP, lo publica con costo cercano a cero y lo consume desde un agente ubicado en cualquier equipo. La arquitectura debe permitir incorporar otros usuarios, mecanismos de autenticacion, proveedores cloud, transportes o persistencia sin reescribir las Tools ni la logica de negocio.

## 2. Decisiones acordadas

1. La Skill se llamara `desarrollar-servidores-mcp`.
2. Se catalogara dentro del stack `ia-llm`, pero podra seleccionarse individualmente.
3. La Skill sera agnostica de Codex, Claude, Cursor, Antigravity y cualquier otro host concreto.
4. El contrato estable sera el protocolo MCP; la configuracion de cada agente sera un adaptador de ultima milla.
5. El enfoque predeterminado sera remoto desde el inicio mediante Streamable HTTP.
6. El desarrollo local ejecutara el mismo servidor HTTP que se despliega; no existira una migracion posterior desde una arquitectura STDIO.
7. STDIO permanecera como transporte opcional cuando el caso de uso lo justifique.
8. El servidor inicial sera stateless siempre que sus herramientas no requieran estado de sesion.
9. El artefacto portable preferido sera un contenedor OCI.
10. Google Cloud Run sera el primer destino documentado y validado, no una dependencia del nucleo.
11. El perfil personal inicial podra usar un bearer token; OAuth 2.1, IAM, IAP, JWT o mTLS seran adaptadores reemplazables.
12. Autenticacion y autorizacion se modelaran como responsabilidades distintas.
13. Las Tools no conoceran encabezados HTTP, proveedores cloud ni detalles del cliente agente.
14. La Skill implementara solamente los adaptadores necesarios para el alcance solicitado; no generara capas vacias especulativas.
15. Ningun despliegue real, alta de facturacion o creacion de recursos cloud se ejecutara sin autorizacion explicita del usuario.

## 3. Alcance

### 3.1 Incluido

- Evaluar si una capacidad debe exponerse mediante MCP.
- Diseñar Tools, Resources y Prompts, priorizando Tools para agregar funciones a agentes.
- Crear contratos de entrada y salida tipados.
- Separar protocolo, transporte, autenticacion, autorizacion, servicios e infraestructura.
- Implementar Streamable HTTP como perfil predeterminado.
- Permitir STDIO como adaptador opcional.
- Preparar ejecucion local y despliegue cloud con el mismo codigo.
- Empaquetar el servidor como contenedor portable cuando el destino lo admita.
- Configurar secretos exclusivamente fuera del codigo y del repositorio.
- Probar contrato MCP, transporte, seguridad y comportamiento funcional.
- Generar instrucciones de conexion por cliente sin contaminar el nucleo.
- Documentar un perfil inicial de Cloud Run con costo controlado.
- Definir caminos de evolucion para autenticacion, persistencia y escalamiento.

### 3.2 Excluido de la primera implementacion

- Crear una plataforma comercial multiusuario.
- Implementar un proveedor OAuth propio completo sin un caso real.
- Mantener adaptadores exhaustivos para todos los proveedores cloud.
- Incluir SDKs de agentes propietarios en el servidor.
- Administrar una maquina virtual o sistema operativo propio.
- Proveer una base de datos si el servidor piloto puede ser stateless.
- Construir una interfaz grafica.
- Publicar el servidor o habilitar facturacion como efecto automatico de la Skill.
- Prometer compatibilidad con clientes que no implementen MCP; se podra documentar un proxy externo como compatibilidad, sin incorporarlo al nucleo.

## 4. Principios arquitectonicos

### 4.1 Invariantes y valores predeterminados

| Categoria | Decision | Naturaleza |
|---|---|---|
| Protocolo | MCP estandar con negociacion de capacidades | Invariante |
| Contratos | Esquemas cerrados y tipados | Invariante |
| Seguridad | Autenticacion y autorizacion fuera del LLM | Invariante |
| Logica | Tools delgadas sobre servicios probables sin MCP | Invariante |
| Portabilidad | Nucleo sin dependencias de un agente o proveedor cloud | Invariante |
| Transporte | Streamable HTTP | Predeterminado reemplazable |
| Ejecucion local | Mismo endpoint HTTP usado en produccion | Predeterminado reemplazable |
| Despliegue | Contenedor OCI en Cloud Run | Predeterminado reemplazable |
| Autenticacion personal | Bearer token | Predeterminado reemplazable |
| Estado | Stateless | Predeterminado reemplazable |
| Lenguaje | Elegido segun el proyecto | Decision contextual |

La Skill debera distinguir expresamente estas dos categorias. No presentara Cloud Run, bearer, Python, TypeScript, FastMCP ni otro SDK como requisito permanente.

### 4.2 Capas del servidor generado

```text
Cliente MCP de cualquier agente
              |
              v
Adaptador de conexion del cliente
              |
              v
Transporte MCP: Streamable HTTP o STDIO
              |
              v
Autenticador -> Identidad -> Autorizador
              |
              v
Handlers MCP: Tools, Resources y Prompts
              |
              v
Servicios de aplicacion
              |
              v
APIs, archivos, bases de datos o sistemas externos
```

La logica de negocio debera poder probarse sin iniciar un servidor MCP. Los handlers convertiran entradas MCP en llamadas a servicios y transformaran sus resultados en salidas MCP estructuradas.

### 4.3 Puntos de extension

- `Autenticador`: convierte credenciales o identidad de plataforma en una identidad interna.
- `Autorizador`: evalua permisos sobre operacion y recurso.
- `Transporte`: publica el mismo servidor mediante HTTP o STDIO.
- `RepositorioEstado`: se incorpora solo cuando una Tool requiera persistencia.
- `AdaptadorInfraestructura`: encapsula APIs, almacenamiento u otros sistemas externos.
- `ConfiguracionDespliegue`: mantiene decisiones del proveedor fuera del nucleo.

No se crearan todas estas abstracciones por anticipado. Cada implementacion debera introducir el punto de extension cuando exista una segunda variante prevista o cuando acoplarlo impida una evolucion ya acordada.

## 5. Diseño de la Skill

### 5.1 Descripcion propuesta

```yaml
---
name: desarrollar-servidores-mcp
description: Diseña, implementa y valida servidores MCP propios que exponen herramientas, recursos o prompts a agentes compatibles. Usar al convertir funciones, APIs o datos internos en capacidades reutilizables mediante MCP. No usar para orquestar agentes ni para scripts locales que no requieren interoperabilidad.
---
```

La invocacion implicita permanecera habilitada. La descripcion debera ser breve y discriminante para no activar la Skill en cualquier tarea que mencione agentes.

### 5.2 Disparadores esperados

- Crear un servidor MCP propio.
- Exponer una API o funcion como Tool MCP.
- Añadir Tools, Resources o Prompts a un servidor MCP existente.
- Convertir un servidor MCP local en remoto sin acoplarlo a un agente.
- Preparar un servidor MCP para despliegue en contenedores o cloud.
- Cambiar autenticacion, transporte o persistencia de un servidor MCP.
- Validar interoperabilidad o seguridad de un servidor MCP.

### 5.3 Exclusiones para evitar solapamientos

- La Skill `agentes-multiagent` continuara diseñando la arquitectura y los limites de agentes que consumen herramientas.
- La Skill `evaluar-agente` continuara evaluando autoridad, prompt injection y tool-use del agente.
- La Skill `seguridad-backend` podra complementar exposicion HTTP sensible, pero no sera una dependencia obligatoria para un prototipo local o privado.
- Un wrapper de una sola ejecucion que no necesite interoperabilidad se resolvera como funcion, biblioteca o CLI convencional.
- La configuracion de un servidor MCP de terceros no activara el flujo completo de desarrollo salvo que el usuario solicite modificarlo o extenderlo.

### 5.4 Divulgacion progresiva

El `SKILL.md` conservara solamente:

- puerta de decision MCP;
- seleccion de modo: nuevo servidor, extension, migracion o auditoria;
- invariantes arquitectonicos y de seguridad;
- criterio para elegir transporte, autenticacion y despliegue;
- flujo de validacion y cierre;
- rutas a referencias especializadas.

Estructura prevista:

```text
desarrollar-servidores-mcp/
├── SKILL.md
└── referencias/
    ├── arquitectura_servidor.md
    ├── diseno_herramientas.md
    ├── seguridad_autenticacion.md
    ├── despliegue_portable.md
    └── pruebas_interoperabilidad.md
```

Cada referencia se leera solo cuando corresponda:

- `arquitectura_servidor.md`: servidores nuevos o refactorizaciones estructurales.
- `diseno_herramientas.md`: diseño o modificacion de Tools, Resources y Prompts.
- `seguridad_autenticacion.md`: cualquier servidor remoto o Tool mutable.
- `despliegue_portable.md`: contenedores, Cloud Run u otro proveedor.
- `pruebas_interoperabilidad.md`: implementacion, migracion o auditoria de conformidad.

No se agregaran assets ni scripts a la primera version sin demostrar una repeticion que justifique automatizacion determinista.

## 6. Arquitectura de referencia para proyectos consumidores

La Skill no impondra una estructura unica, pero podra proponer esta organizacion cuando el proyecto no tenga una convencion equivalente:

```text
servidor_mcp/
├── pyproject.toml o package.json
├── Dockerfile
├── src/
│   └── servidor_mcp/
│       ├── aplicacion.py o aplicacion.ts
│       ├── configuracion.py o configuracion.ts
│       ├── autenticacion/
│       ├── autorizacion/
│       ├── herramientas/
│       ├── recursos/
│       ├── servicios/
│       ├── esquemas/
│       └── transportes/
├── pruebas/
└── despliegue/
```

Los nombres impuestos por herramientas, como `Dockerfile`, `pyproject.toml`, `package.json` o campos del protocolo MCP, se documentaran como excepciones nominales cuando el framework todavia no las contemple.

## 7. Perfiles operativos

| Perfil | Transporte | Autenticacion | Estado | Destino |
|---|---|---|---|---|
| Desarrollo remoto-compatible | HTTP local | Deshabilitada solo en loopback | Stateless | Equipo local |
| Personal remoto | HTTPS | Bearer token rotatorio | Stateless | Cloud Run u otro contenedor administrado |
| Equipo privado | HTTPS | IAM, IAP, JWT o proveedor corporativo | Segun necesidad | Cloud privado |
| Multiusuario | HTTPS | OAuth 2.1 con scopes | Persistencia explicita | Servicio administrado escalable |
| Servicio a servicio | HTTPS | Identidad de carga o mTLS | Segun necesidad | Infraestructura interna |
| Compatibilidad local | STDIO | Entorno local | Por proceso | Cliente sin transporte remoto |

El perfil inicial del piloto sera `personal remoto`. La transicion a otro perfil no debera modificar Tools ni servicios de aplicacion.

## 8. Estrategia cloud-first y portable

### 8.1 Perfil inicial de Cloud Run

- Streamable HTTP con endpoint `/mcp`.
- Facturacion por solicitudes.
- Cero instancias minimas.
- Una instancia maxima durante el piloto.
- Recursos minimos compatibles con el runtime.
- Una sola region.
- Contenedor o despliegue desde fuente reproducible.
- Logs estructurados sin secretos ni payloads sensibles.
- Secreto de autenticacion administrado fuera de Git.
- Pruebas negativas para token ausente, incorrecto y revocado.
- Alerta de presupuesto documentada; se aclarara que una alerta no detiene el gasto.

### 8.2 Portabilidad

El servidor debera cumplir el contrato de un contenedor HTTP convencional:

- escuchar en la interfaz y puerto entregados por el entorno;
- no depender de disco persistente local;
- no guardar sesiones criticas solamente en memoria si se habilitan varias instancias;
- terminar limpiamente al recibir la señal del proveedor;
- usar variables o secretos externos para configuracion;
- disponer de una comprobacion de salud que no exponga Tools ni informacion sensible;
- mantener toda configuracion de Google Cloud dentro de `despliegue/` o automatizacion equivalente.

Migrar entre plataformas que ejecutan contenedores debera requerir principalmente configuracion. Un runtime propietario, como un entorno edge sin contenedores, podra requerir un adaptador de transporte; el nucleo, las Tools, los esquemas y los servicios deberan seguir siendo reutilizables.

### 8.3 Control de costos

- No establecer instancias minimas mayores que cero durante el piloto.
- Limitar instancias maximas y concurrencia de acuerdo con el comportamiento medido.
- Evitar balanceadores, conectores VPC, bases de datos y dominios personalizados hasta que sean necesarios.
- Registrar todos los componentes facturables habilitados.
- Ejecutar una prueba de carga acotada, nunca abierta o indefinida.
- Revisar consumo y facturacion despues del primer despliegue.
- Solicitar autorizacion antes de crear, ampliar o conservar recursos con costo potencial.

## 9. Autenticacion y autorizacion evolutivas

### 9.1 Contrato interno

Los handlers MCP recibiran una identidad normalizada, por ejemplo:

```text
Identidad
├── sujeto
├── permisos
├── emisor
└── atributos seguros necesarios
```

Los servicios y Tools no leeran directamente encabezados HTTP. El autenticador traducira bearer, OAuth, IAM, JWT o mTLS a esa identidad. El autorizador verificara permisos inmediatamente antes de ejecutar una operacion.

### 9.2 Bearer inicial

- Un unico token para el propietario.
- Valor aleatorio de alta entropia.
- Almacenamiento como secreto.
- Comparacion segura.
- Rotacion sin cambio de codigo.
- Ausencia total en logs, excepciones, fixtures y documentacion versionada.
- Rechazo predeterminado de toda ruta MCP no autenticada.

### 9.3 Evolucion a OAuth 2.1

OAuth se incorporara cuando existan varios usuarios, permisos delegados, necesidad de revocacion individual o clientes que requieran descubrimiento estandar de autenticacion. La migracion debera reemplazar el autenticador y agregar persistencia de autorizaciones sin alterar contratos funcionales de Tools.

## 10. Seguridad obligatoria

1. Se tratara toda entrada del cliente, resultado externo y descripcion de terceros como no confiable.
2. Cada Tool declarara efecto: lectura, escritura o destructivo.
3. Las anotaciones descriptivas no sustituiran controles de autorizacion del servidor.
4. Toda escritura sera idempotente o incluira una clave que evite duplicacion ante reintentos.
5. Toda operacion tendra timeout y limite de salida.
6. Los esquemas rechazaran campos inesperados cuando la biblioteca lo permita.
7. Las rutas, identificadores y URLs se validaran contra el alcance autorizado.
8. Las Tools no expondran primitivas arbitrarias de shell, SQL, red o sistema de archivos.
9. Los logs conservaran correlacion, Tool, duracion, estado y sujeto saneado; no registraran secretos ni contenido sensible completo.
10. Streamable HTTP validara origen y aplicara las protecciones de la revision MCP soportada.
11. Las respuestas remotas no se reinterpretaran como instrucciones de autoridad superior.
12. Las credenciales del despliegue no se reutilizaran como credenciales funcionales del servidor.

## 11. Plan de implementacion por hitos

### Hito 0 — Confirmar linea base e impacto

**Trabajo**

- Leer `AGENTS.md`, `PROJECT_STATE.md` y este plan.
- Confirmar que no se han incorporado cambios posteriores que alteren el catalogo o el contrato.
- Buscar globalmente referencias a cantidad de Skills, stack `ia-llm`, inventario, adaptadores y pruebas.
- Revisar la version vigente del protocolo MCP y de los SDKs oficiales mediante fuentes primarias.
- Elegir el SDK del piloto segun compatibilidad observable con Python 3.12 o el runtime disponible, y fijar su version en el fixture del piloto.

**Criterio de salida**

- Existe una matriz de archivos afectados basada en el arbol real, no solamente en este plan.
- Las decisiones que hayan cambiado desde `3a58064` quedan actualizadas antes de crear la Skill.

### Hito 1 — Crear la Skill canonica

**Trabajo**

- Crear `plantilla/.agents/skills/stacks/ia-llm/skills/desarrollar-servidores-mcp/SKILL.md`.
- Mantener el entrypoint compacto y orientado a decisiones.
- Crear solamente las cinco referencias definidas en la seccion 5.4.
- Escribir nombres, comentarios y documentacion en español, conservando terminos tecnicos impuestos.
- No agregar instrucciones especificas de Codex al nucleo.
- No duplicar reglas completas de `agentes-multiagent`, `evaluar-agente` o `seguridad-backend`; enlazar esas Skills solo de forma condicional.

**Criterio de salida**

- `quick_validate.py` aprueba la nueva Skill.
- La descripcion activa los casos MCP y excluye orquestacion de agentes y scripts convencionales.
- Cada referencia tiene un llamador explicito desde `SKILL.md`.
- No existen placeholders ni carpetas sin uso.

### Hito 2 — Integrar catalogo, stack y adaptadores del framework

**Trabajo**

- Actualizar `plantilla/.agents/skills/stacks/ia-llm/LEEME.md` con la nueva Skill, proposito, seleccion y procedencia original.
- Actualizar el inventario narrativo y la cantidad total en `README.md`.
- Actualizar `PROJECT_STATE.md` con implementacion, tecnologias y siguiente paso.
- Revisar `plantilla/.agents/rules/excepciones_nominales.md` para nombres impuestos por MCP, SDK, contenedor y despliegue.
- Regenerar wrappers Claude mediante el flujo canonico existente.
- Confirmar que creacion, adicion posterior y actualizacion conservadora incluyen la Skill sin constantes paralelas.
- Regenerar `auditoria/inventario_skills.json` mediante su script oficial.
- Revisar `ATRIBUCIONES.md`; registrar que el contenido es original y que usa especificaciones oficiales como referencia, sin atribuirlo a un plugin externo.

**Criterio de salida**

- El catalogo enumera la nueva Skill con categoria y stack correctos.
- Una instancia nueva puede seleccionarla individualmente.
- Una instancia existente puede agregarla transaccionalmente.
- Los wrappers remiten a la fuente canonica sin copiar instrucciones.
- Ninguna cantidad o lista documental permanece en 23 Skills.

### Hito 3 — Ampliar pruebas deterministas del framework

**Trabajo**

- Actualizar pruebas de calidad, catalogo, creacion, adicion y actualizacion.
- Comprobar que la Skill se instala sola sin arrastrar Skills hermanas.
- Comprobar que las referencias acompañan a `SKILL.md` y conservan sus huellas.
- Comprobar que una modificacion local en una referencia bloquea la actualizacion conservadora.
- Añadir invariantes semanticas utiles: agnosticismo del agente, separacion autenticacion/autorizacion, Streamable HTTP predeterminado reemplazable, contenedor portable y autorizacion antes de desplegar.
- Evitar pruebas que solo busquen encabezados o redaccion exacta sin validar comportamiento estructural.

**Criterio de salida**

- Las pruebas focalizadas aprueban en Python 3.9 y 3.12 cuando corresponda.
- No se agregan dependencias de runtime MCP a las pruebas estructurales del framework.

### Hito 4 — Construir un piloto aislado

**Trabajo**

- Crear un fixture temporal o proyecto piloto generado mediante la nueva Skill.
- Usar Python 3.12 como primera opcion del piloto, sin convertirlo en requisito de la Skill.
- Implementar una Tool de solo lectura y una Tool mutable idempotente.
- Separar servicios, identidad, autenticador bearer, autorizador, handlers MCP y transporte HTTP.
- Ejecutar el mismo endpoint `/mcp` en desarrollo y en el artefacto desplegable.
- Incorporar contenedor, configuracion tipada y secretos externos.
- Mantener el piloto fuera del catalogo distribuible salvo que se decida convertirlo en fixture permanente.

**Criterio de salida**

- El servidor inicia localmente mediante Streamable HTTP.
- La logica de negocio se prueba sin MCP.
- El cliente de prueba descubre e invoca ambas Tools.
- Las solicitudes sin permiso no producen efectos.
- La repeticion de la Tool mutable no duplica el efecto.

### Hito 5 — Validar protocolo, transporte y seguridad

**Trabajo**

- Ejecutar pruebas unitarias de servicios y esquemas.
- Ejecutar pruebas de contrato con un cliente MCP generico o cliente en memoria del SDK.
- Validar inicializacion, negociacion de capacidades, listado y llamada de Tools.
- Validar respuestas estructuradas y errores MCP.
- Probar token ausente, incorrecto, correcto y rotado.
- Probar timeout, cancelacion o corte del cliente cuando el SDK lo soporte.
- Probar limite de salida y resultado externo malicioso.
- Ejecutar MCP Inspector contra el endpoint local.
- Construir y ejecutar el contenedor cuando Docker este disponible.

**Criterio de salida**

- Todas las pruebas funcionales y negativas aprueban.
- El contenedor expone el mismo comportamiento observado fuera de el.
- No se filtran secretos en logs ni respuestas.

### Hito 6 — Validar Cloud Run con costo controlado

**Precondicion**

- Obtener autorizacion explicita del usuario para habilitar o usar facturacion, crear recursos y desplegar.

**Trabajo**

- Crear un proyecto o seleccionar uno confirmado por el usuario.
- Habilitar solamente las APIs necesarias.
- Desplegar con cero instancias minimas y una maxima.
- Configurar el secreto sin escribir su valor en comandos registrables cuando exista una alternativa segura.
- Confirmar HTTPS, endpoint, health check y logs.
- Ejecutar pruebas remotas positivas y negativas.
- Revisar consumo y componentes facturables.
- Registrar comandos reproducibles sin credenciales.
- Preguntar antes de conservar o eliminar recursos materiales.

**Criterio de salida**

- El mismo cliente de prueba local invoca el servidor remoto cambiando solamente URL y credenciales.
- El endpoint sin token y con token invalido queda rechazado.
- La Tool mutable conserva autorizacion e idempotencia.
- El costo observado y los recursos activos quedan documentados.

### Hito 7 — Validar independencia del agente

**Trabajo**

- Probar primero con MCP Inspector o un cliente generico como evidencia principal.
- Conectar al menos un agente real que soporte MCP remoto.
- Conectar un segundo cliente diferente cuando este disponible; puede usar un proxy local si carece de Streamable HTTP.
- Mantener configuraciones de clientes fuera del servidor.
- Comparar descubrimiento de Tools, argumentos, resultados y errores.
- Registrar limitaciones del cliente sin convertirlas en reglas universales del servidor.

**Criterio de salida**

- Ninguna modificacion del nucleo es necesaria para cambiar de cliente.
- Las diferencias se limitan a URL, autenticacion o adaptador de configuracion.
- No se afirma compatibilidad con un agente que no se haya probado.

### Hito 8 — Cerrar, documentar y publicar

**Trabajo**

- Actualizar este plan con resultados y desviaciones reales.
- Actualizar `PROJECT_STATE.md`, `README.md`, stack, inventario y atribuciones finales.
- Ejecutar `python scripts/validar_cierre_cambio.py`.
- Ejecutar la CI completa en Windows y Ubuntu.
- Registrar por separado pruebas locales, pruebas simuladas y despliegue real.
- Crear commits pequeños por hito o por unidad coherente.
- No declarar la Skill eficaz hasta que el piloto funcional y la prueba multiagente aprueben.

**Criterio de salida**

- La puerta automatica de cierre aprueba.
- CI remota aprueba.
- Un proyecto nuevo y uno existente reciben la Skill correctamente.
- El piloto demuestra desarrollo HTTP local, despliegue remoto y consumo por un agente sin reescritura.

## 12. Matriz prevista de archivos afectados

| Area | Archivos o rutas a revisar |
|---|---|
| Skill | `plantilla/.agents/skills/stacks/ia-llm/skills/desarrollar-servidores-mcp/**` |
| Stack | `plantilla/.agents/skills/stacks/ia-llm/LEEME.md` |
| Catalogo | `README.md`, `scripts/catalogo_skills.py`, `auditoria/inventario_skills.json` |
| Estado | `PROJECT_STATE.md`, este plan |
| Adaptadores | `plantilla/scripts/sincronizar_adaptadores_agentes.py`, wrappers generados y sus pruebas |
| Contrato | `plantilla/configuracion_plantilla.json` solo si se agrega un script distribuido |
| Excepciones | `plantilla/.agents/rules/excepciones_nominales.md` |
| Atribuciones | `ATRIBUCIONES.md` y catalogo narrativo cuando corresponda |
| Pruebas | calidad de Skills, catalogo, creacion, adicion, actualizacion, compatibilidad de agentes y cierre |
| CI | workflow existente y posible trabajo aislado del piloto MCP |

La busqueda del Hito 0 prevalecera sobre esta lista si descubre consumidores adicionales.

## 13. Estrategia de pruebas

| Nivel | Objetivo | Debe ejecutarse sin nube |
|---|---|---|
| Estructural | Frontmatter, rutas, referencias y catalogo | Si |
| Distribucion | Creacion, adicion, actualizacion y huellas | Si |
| Unitario | Servicios, esquemas y autorizacion | Si |
| Contrato MCP | Capacidades, Tools y resultados | Si |
| Transporte | Endpoint Streamable HTTP | Si |
| Seguridad | Credenciales, permisos, limites y reintentos | Si |
| Contenedor | Mismo comportamiento en imagen OCI | Si, cuando Docker este disponible |
| Nube | HTTPS, secretos, escalamiento y logs | No |
| Interoperabilidad | Cliente generico y agentes reales | Parcialmente |

Las pruebas cloud no sustituiran las deterministas. La suite comun del framework no dependera de credenciales, red ni facturacion.

## 14. Criterios globales de aceptacion

La implementacion se considerara completa solamente cuando:

1. La Skill pueda instalarse individualmente desde el catalogo.
2. Su nucleo no nombre ni requiera un agente concreto.
3. Streamable HTTP sea el valor predeterminado, no una restriccion.
4. Cloud Run sea un adaptador documentado, no una dependencia funcional.
5. Bearer sea reemplazable sin modificar Tools ni servicios.
6. Autenticacion y autorizacion tengan responsabilidades separadas.
7. El servidor piloto use el mismo codigo local y remoto.
8. Un cliente MCP generico valide el contrato.
9. Al menos un agente real consuma el servidor remoto.
10. Un segundo cliente demuestre portabilidad o documente una limitacion real del host.
11. La configuracion cloud limite costo y escalamiento inicial.
12. No existan secretos versionados ni expuestos en logs.
13. Proyectos nuevos y existentes reciban Skill y referencias sin sobrescribir cambios locales.
14. Documentacion, inventario y cantidades sean coherentes.
15. `python scripts/validar_cierre_cambio.py` y CI remota aprueben.

## 15. Riesgos y mitigaciones

| Riesgo | Mitigacion |
|---|---|
| Acoplamiento a Cloud Run | Contenedor OCI y configuracion cloud fuera del nucleo |
| Acoplamiento a Codex | Contrato MCP y prueba con cliente generico antes de agentes reales |
| Capa gratuita superada | Cero instancias minimas, una maxima, alertas y revision posterior |
| Cliente sin MCP remoto | Proxy de compatibilidad o transporte STDIO opcional |
| Bearer filtrado | Secreto externo, saneamiento de logs y rotacion probada |
| Doble ejecucion por reintento | Idempotencia y claves de operacion |
| Estado perdido al escalar | Stateless inicial o repositorio compartido explicito |
| SDK o protocolo cambiante | Consultar fuentes primarias y fijar versiones en el piloto |
| Tool demasiado poderosa | Operaciones pequeñas, esquema cerrado y autorizacion por recurso |
| Skill demasiado extensa | Entry point compacto y referencias bajo demanda |
| Pruebas que solo validan texto | Piloto funcional, cliente MCP y verificaciones de efectos |

## 16. Protocolo de ejecucion para cualquier agente

El agente que retome este trabajo debera:

1. Leer `AGENTS.md`, `PROJECT_STATE.md` y este plan antes de editar.
2. Verificar la linea base y cambios locales del usuario.
3. Ejecutar los hitos en orden, salvo que documente una dependencia que justifique alterarlo.
4. Actualizar este plan al cerrar cada hito con evidencia y rutas concretas.
5. Mantener los placeholders de `plantilla/` sin instanciar.
6. Incorporar cualquier script distribuido al contrato `archivos_gestionados`.
7. Usar fuentes oficiales actuales para MCP, SDK y proveedor cloud.
8. Solicitar autorizacion antes de facturacion, despliegue o cambios externos.
9. Separar claramente simulacion, prueba local, prueba remota y medicion de costo.
10. Ejecutar la puerta de cierre antes de declarar terminado el cambio.

## 17. Orden sugerido de commits

1. `docs: define plan para servidores MCP remotos`
2. `feat: agrega skill para desarrollar servidores MCP`
3. `test: valida distribucion y coherencia de la skill MCP`
4. `test: incorpora piloto funcional de servidor MCP remoto`
5. `docs: registra validacion cloud y multiagente`

Los commits 4 y 5 podran dividirse si la validacion externa requiere aprobacion o se ejecuta en otra sesion.

## 18. Fuentes primarias de referencia

- Especificacion MCP vigente al ejecutar el Hito 0: <https://modelcontextprotocol.io/specification/2026-07-28>
- Anuncio y cambios de MCP 2026-07-28: <https://blog.modelcontextprotocol.io/posts/2026-07-28/>
- SDK oficial de Python: <https://py.sdk.modelcontextprotocol.io/get-started/>
- Despliegue y escalamiento con el SDK oficial de Python: <https://py.sdk.modelcontextprotocol.io/run/deploy/>
- Servidores MCP en Cloud Run: <https://docs.cloud.google.com/run/docs/host-mcp-servers>
- Tutorial remoto de Cloud Run: <https://docs.cloud.google.com/run/docs/tutorials/deploy-remote-mcp-server>
- Precios de Cloud Run: <https://cloud.google.com/run/pricing>

Las revisiones fechadas se volveran a comprobar durante la implementacion. El plan no congela una version de SDK que aun no haya sido validada en el piloto.
