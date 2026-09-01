import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("la página conserva el contenido verificable", async () => {
  const contenido = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
  assert.match(contenido, /Fixture Next\.js válido/);
});
