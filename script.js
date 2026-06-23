const formulario = document.getElementById("formRegistro");
const lista = document.getElementById("listaRegistros");
const mensaje = document.getElementById("mensaje");
const contador = document.getElementById("contador");

let total = 0;

formulario.addEventListener("submit", function(event) {

    event.preventDefault();

    const nombre = document.getElementById("nombre").value.trim();
    const descripcion = document.getElementById("descripcion").value.trim();
    const categoria = document.getElementById("categoria").value.trim();

    if (nombre === "" || descripcion === "" || categoria === "") {

        mensaje.innerHTML =
        '<div class="alert alert-danger">Todos los campos son obligatorios.</div>';

        return;
    }

    mensaje.innerHTML =
    '<div class="alert alert-success">Registro agregado correctamente.</div>';

    const tarjeta = document.createElement("div");
    tarjeta.className = "card p-3 m-3";

    const titulo = document.createElement("h4");
    titulo.textContent = nombre;

    const texto = document.createElement("p");
    texto.textContent = descripcion;

    const tipo = document.createElement("p");
    tipo.innerHTML = "<strong>Categoría:</strong> " + categoria;

    const boton = document.createElement("button");
    boton.textContent = "Eliminar";
    boton.className = "btn btn-danger";

    boton.addEventListener("click", function() {

        tarjeta.remove();

        total--;

        contador.textContent = total;
    });

    tarjeta.appendChild(titulo);
    tarjeta.appendChild(texto);
    tarjeta.appendChild(tipo);
    tarjeta.appendChild(boton);

    lista.appendChild(tarjeta);

    total++;

    contador.textContent = total;

    formulario.reset();

});