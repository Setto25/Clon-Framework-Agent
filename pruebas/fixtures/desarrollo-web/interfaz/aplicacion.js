const lista = document.querySelector("#lista-tareas");

async function cargarTareas() {
  const respuesta = await fetch("/api/tareas");
  const tareas = await respuesta.json();
  lista.replaceChildren(
    ...tareas.map((tarea) => {
      const elemento = document.createElement("li");
      elemento.textContent = tarea.titulo;
      return elemento;
    }),
  );
}

cargarTareas();
