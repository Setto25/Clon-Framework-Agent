import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const raiz = new URL("../interfaz/", import.meta.url);

test("la interfaz permite crear y filtrar tareas", async () => {
  const html = await readFile(new URL("interfaz.html", raiz), "utf8");
  assert.match(html, /<form[^>]+id=["']formulario-tarea["']/i);
  assert.match(html, /<label[^>]+for=["']titulo-tarea["']/i);
  assert.match(html, /data-filtro=["']todas["']/i);
  assert.match(html, /data-filtro=["']pendientes["']/i);
  assert.match(html, /data-filtro=["']completadas["']/i);
  assert.match(html, /aria-live=["']polite["']/i);
});

test("el cliente integra creacion y cambio de estado con la API", async () => {
  const javascript = await readFile(new URL("aplicacion.js", raiz), "utf8");
  assert.match(javascript, /method\s*:\s*["']POST["']/i);
  assert.match(javascript, /method\s*:\s*["']PATCH["']/i);
  assert.match(javascript, /JSON\.stringify/);
  assert.match(javascript, /preventDefault\s*\(/);
  assert.match(javascript, /completada/);
  assert.match(javascript, /filtro/i);
});
