---
name: seguridad-backend
description: Diseña, revisa y endurece la seguridad de backends HTTP y APIs antes de exponerlos a red o procesar datos sensibles. Usar al definir autenticacion, autorizacion, endpoints con recursos por usuario, integraciones externas o criterios de release. No usar como sustituto de una auditoria especializada ni para afirmar seguridad sin pruebas.
---

# Seguridad de backend

Esta Skill convierte riesgos concretos en controles y pruebas. No aplica una lista universal ni declara un sistema seguro solo porque una comprobacion estatica apruebe.

## Preparar el alcance

Antes de cambiar codigo se confirma:

- exposicion prevista: local, red privada, Internet o servicio a servicio;
- actores, roles, tenants y recursos que pertenecen a cada identidad;
- datos sensibles, secretos y operaciones irreversibles;
- limites de confianza entre cliente, backend, base de datos, colas y proveedores;
- framework, versiones, proxy, terminacion TLS y controles ya existentes.

Si faltan decisiones de identidad, propiedad de datos o exposicion, se documenta el bloqueo. No se inventa un esquema de autenticacion ni se expone el servicio como parte implicita de la tarea.

## Modelar antes de implementar

Se crea una matriz minima por endpoint o caso de uso con:

| Campo | Pregunta verificable |
|---|---|
| Actor | Quien puede iniciar la operacion |
| Autenticacion | Como se comprueba su identidad |
| Funcion | Que rol o permiso habilita la accion |
| Objeto | Como se comprueba que puede operar sobre ese recurso concreto |
| Propiedades | Que campos puede leer o modificar |
| Limites | Que volumen, frecuencia, tamaño y tiempo se permiten |
| Datos | Que informacion acepta, registra y devuelve |
| Dependencias | Que proveedor, URL, archivo o mensaje externo consume |

Las reglas de autorizacion se aplican en el servidor y niegan por defecto. Un router protegido no demuestra por si solo autorizacion sobre cada objeto.

## Seleccionar controles por riesgo

Se lee [referencias/controles_backend.md](referencias/controles_backend.md) para cualquier backend HTTP o API. Si el proyecto usa FastAPI, tambien se lee [referencias/fastapi.md](referencias/fastapi.md).

Se implementan solamente controles pertinentes al alcance confirmado. Como base:

- la entrada se valida mediante esquemas permitidos y la salida expone solo campos autorizados;
- las consultas usan parametros o un ORM sin concatenar entrada como codigo;
- secretos y credenciales no tienen valores utilizables por defecto ni aparecen en logs o respuestas;
- errores externos no revelan trazas, consultas, rutas internas o configuracion;
- CORS, hosts, metodos, contenidos y documentacion se restringen segun el ambiente;
- consumo, concurrencia, tamaño y tiempo tienen limites donde un abuso pueda degradar el servicio;
- URLs, webhooks, archivos y respuestas de terceros se tratan como entrada no confiable;
- dependencias y lock files se revisan con herramientas compatibles con el proyecto.

## Probar controles

Cada control relevante incluye una prueba que falle antes de implementarlo. Se priorizan:

1. solicitud sin identidad y con credencial invalida;
2. rol insuficiente para una funcion privilegiada;
3. una identidad intentando leer o modificar el recurso de otra;
4. campos de entrada o salida no autorizados;
5. limites, tamaños, formatos y transiciones invalidas;
6. secretos, detalles internos o datos sensibles ausentes de errores y logs;
7. fallos y respuestas inesperadas de dependencias externas.

Los escaneres complementan estas pruebas; no sustituyen la verificacion de reglas de negocio ni de propiedad de objetos. No se ejecutan pruebas intrusivas contra sistemas compartidos o productivos sin autorizacion explicita.

## Puerta de exposicion

Antes de recomendar despliegue o exposicion se entrega evidencia con:

- alcance y matriz de autorizacion revisados;
- controles implementados y rutas afectadas;
- comandos y resultados de pruebas;
- hallazgos abiertos, severidad, responsable y decision;
- controles delegados al proxy, plataforma o infraestructura que no se verificaron localmente.

Una omision que permita eludir autenticacion o autorizacion, filtrar secretos, inyectar consultas o acceder a datos ajenos bloquea la recomendacion de exposicion. Cualquier aceptacion de riesgo debe corresponder a una decision humana explicita y quedar documentada.

## Referencias de criterio

La Skill usa como referencias de criterio OWASP ASVS 5.0.0, OWASP API Security Top 10 2023, OWASP REST Security Cheat Sheet y la documentacion oficial del framework utilizado. Se registra la version consultada; no se asume que una lista resumida sustituya el estandar completo.
