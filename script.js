const formulario = document.getElementById("formRegistro");
const lista = document.getElementById("listaRegistros");
const mensaje = document.getElementById("mensaje");
const contador = document.getElementById("contador");


const nombre = document.getElementById("nombre");
const descripcion = document.getElementById("descripcion");
const categoria = document.getElementById("categoria");


let total = 0;


function validarNombre(){

    if(nombre.value.trim().length < 5){

        nombre.classList.add("is-invalid");
        nombre.classList.remove("is-valid");

        document.getElementById("errorNombre").textContent =
        "El nombre debe tener al menos 5 caracteres.";

        return false;
    }

    nombre.classList.remove("is-invalid");
    nombre.classList.add("is-valid");

    document.getElementById("errorNombre").textContent = "";

    return true;
}

function validarDescripcion(){

    if(descripcion.value.trim().length < 10){

        descripcion.classList.add("is-invalid");
        descripcion.classList.remove("is-valid");

        document.getElementById("errorDescripcion").textContent =
        "La descripción debe tener al menos 10 caracteres.";

        return false;
    }

    descripcion.classList.remove("is-invalid");
    descripcion.classList.add("is-valid");

    document.getElementById("errorDescripcion").textContent = "";

    return true;
}

function validarCategoria(){

    if(categoria.value === ""){

        categoria.classList.add("is-invalid");
        categoria.classList.remove("is-valid");

        document.getElementById("errorCategoria").textContent =
        "Seleccione una categoría.";

        return false;
    }

    categoria.classList.remove("is-invalid");
    categoria.classList.add("is-valid");

    document.getElementById("errorCategoria").textContent = "";

    return true;
}





nombre.addEventListener("input", validarNombre);
nombre.addEventListener("blur", validarNombre);

descripcion.addEventListener("input", validarDescripcion);
descripcion.addEventListener("blur", validarDescripcion);

categoria.addEventListener("change", validarCategoria);

formulario.addEventListener("submit", function(event) {


    event.preventDefault();

    const correcto =
validarNombre() &&
validarDescripcion() &&
validarCategoria();

if(!correcto){

    mensaje.innerHTML =
    '<div class="alert alert-danger">Corrija los errores antes de registrar.</div>';

    return;
}



    mensaje.innerHTML =
    '<div class="alert alert-success">Registro agregado correctamente.</div>';

    const tarjeta = document.createElement("div");
    tarjeta.className = "card p-3 m-3";


    const titulo = document.createElement("h4");
    titulo.textContent = nombre.value;

    const texto = document.createElement("p");
    texto.textContent = descripcion.value;

    const tipo = document.createElement("p");
    tipo.innerHTML = "<strong>Categoría:</strong> " + categoria.value;




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

    mensaje.innerHTML =
'<div class="alert alert-success">Registro agregado correctamente.</div>';

    formulario.reset();

    nombre.classList.remove("is-valid");
    descripcion.classList.remove("is-valid");
    categoria.classList.remove("is-valid");

    document.getElementById("errorNombre").textContent = "";
    document.getElementById("errorDescripcion").textContent = "";
    document.getElementById("errorCategoria").textContent = "";


setTimeout(function () {
    mensaje.innerHTML = "";
}, 3000);

});