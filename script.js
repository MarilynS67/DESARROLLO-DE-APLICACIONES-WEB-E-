const formulario = document.getElementById("formRegistro");
const lista = document.getElementById("listaRegistros");
const mensaje = document.getElementById("mensaje");
const contador = document.getElementById("contador");


const nombre = document.getElementById("nombre");
const descripcion = document.getElementById("descripcion");
const categoria = document.getElementById("categoria");



let registros = [];

function mostrarRegistros(){

    lista.innerHTML = "";

    if(registros.length === 0){

        lista.innerHTML =
        '<div class="alert alert-warning">No existen registros.</div>';

        contador.textContent = 0;

        return;
    }

    registros.forEach(function(registro, indice){

        const tarjeta = document.createElement("div");
        tarjeta.className = "card p-3 m-3";

        tarjeta.innerHTML = `
            <h4>${registro.nombre}</h4>
            <p>${registro.descripcion}</p>
            <p><strong>Categoría:</strong> ${registro.categoria}</p>
            <button class="btn btn-danger">Eliminar</button>
        `;

        tarjeta.querySelector("button").addEventListener("click", function(){

            registros.splice(indice, 1);

            mostrarRegistros();

        });

        lista.appendChild(tarjeta);

    });

    contador.textContent = registros.length;

}


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

    const nuevoRegistro = {

    nombre: nombre.value,

    descripcion: descripcion.value,

    categoria: categoria.value

};

registros.push(nuevoRegistro);

mostrarRegistros();



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