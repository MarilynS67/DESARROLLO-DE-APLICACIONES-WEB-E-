import os
from flask import Flask, render_template, redirect, url_for, flash

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import generate_password_hash, check_password_hash

from psycopg2 import IntegrityError
from psycopg2.extras import RealDictCursor

from conexion.conexion_postgresql import obtener_conexion

from forms.cliente_form import ClienteForm
from forms.producto_form import ProductoForm
from forms.proveedor_form import ProveedorForm
from forms.facturacion_form import FacturacionForm
from forms.login_form import LoginForm
from forms.usuario_form import UsuarioForm

from models import Usuario


# ==========================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ==========================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

nombre_sistema = "Sistema de Desarrollo Web"


# ==========================================================
# CONFIGURACIÓN DE FLASK-LOGIN
# ==========================================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

login_manager.login_message = (
    "Debe iniciar sesión para acceder a esta página."
)

login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):

    conn = obtener_conexion()

    cursor = conn.cursor(
        cursor_factory=RealDictCursor
    )

    cursor.execute(
        """
        SELECT id, usuario, password
        FROM usuarios
        WHERE id = %s
        """,
        (user_id,)
    )

    datos_usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    if datos_usuario:

        return Usuario(
            datos_usuario["id"],
            datos_usuario["usuario"],
            datos_usuario["password"]
        )

    return None


# ==========================================================
# INICIO
# ==========================================================

@app.route("/")
def inicio():

    return render_template(
        "index.html"
    )


# ==========================================================
# REGISTRO DE USUARIO
# ==========================================================

@app.route(
    "/registro",
    methods=["GET", "POST"]
)
def registro():

    form = UsuarioForm()

    if form.validate_on_submit():

        password_hash = generate_password_hash(
            form.password.data
        )

        conn = obtener_conexion()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO usuarios
                (usuario, password)
                VALUES (%s, %s)
                """,
                (
                    form.usuario.data,
                    password_hash
                )
            )

            conn.commit()

            flash(
                "Usuario registrado correctamente. "
                "Ahora puede iniciar sesión.",
                "success"
            )

            return redirect(
                url_for("login")
            )

        except IntegrityError:

            conn.rollback()

            flash(
                "El nombre de usuario ya existe. "
                "Elija otro.",
                "danger"
            )

        finally:

            cursor.close()
            conn.close()

    return render_template(
        "registro.html",
        form=form
    )


# ==========================================================
# LOGIN
# ==========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if current_user.is_authenticated:

        return redirect(
            url_for("dashboard")
        )

    form = LoginForm()

    if form.validate_on_submit():

        conn = obtener_conexion()

        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute(
            """
            SELECT id, usuario, password
            FROM usuarios
            WHERE usuario = %s
            """,
            (form.usuario.data,)
        )

        datos_usuario = cursor.fetchone()

        cursor.close()
        conn.close()

        if datos_usuario and check_password_hash(
            datos_usuario["password"],
            form.password.data
        ):

            usuario = Usuario(
                datos_usuario["id"],
                datos_usuario["usuario"],
                datos_usuario["password"]
            )

            login_user(usuario)

            flash(
                "Inicio de sesión exitoso.",
                "success"
            )

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Usuario o contraseña incorrectos.",
            "danger"
        )

    return render_template(
        "login.html",
        form=form
    )


# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "dashboard.html",
        nombre_sistema=nombre_sistema
    )


# ==========================================================
# CERRAR SESIÓN
# ==========================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "Sesión cerrada correctamente.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# ==========================================================
# PRODUCTOS - LISTAR Y AGREGAR
# ==========================================================

@app.route(
    "/productos",
    methods=["GET", "POST"]
)
@login_required
def productos():

    form = ProductoForm()

    conn = obtener_conexion()

    cursor = conn.cursor(
        cursor_factory=RealDictCursor
    )

    if form.validate_on_submit():

        cursor.execute(
            """
            INSERT INTO productos
            (
                nombre,
                descripcion,
                precio,
                stock
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                form.nombre.data,
                form.descripcion.data,
                float(form.precio.data),
                form.stock.data
            )
        )

        conn.commit()

        cursor.close()
        conn.close()

        flash(
            "Producto registrado correctamente.",
            "success"
        )

        return redirect(
            url_for("productos")
        )

    cursor.execute(
        """
        SELECT
            p.id,
            p.nombre,
            p.descripcion,
            p.precio,
            p.stock,
            pr.nombre AS proveedor_nombre
        FROM productos p
        LEFT JOIN proveedores pr
            ON p.id_proveedor = pr.id_proveedor
        ORDER BY p.id DESC
        """
    )

    productos_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "productos.html",
        nombre_sistema=nombre_sistema,
        productos=productos_data,
        form=form
    )


# ==========================================================
# PRODUCTOS - MODIFICAR
# ==========================================================

@app.route(
    "/productos/editar/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def editar_producto(id):

    conn = obtener_conexion()

    cursor = conn.cursor(
        cursor_factory=RealDictCursor
    )

    cursor.execute(
        """
        SELECT *
        FROM productos
        WHERE id = %s
        """,
        (id,)
    )

    producto = cursor.fetchone()

    if producto is None:

        cursor.close()
        conn.close()

        return redirect(
            url_for("productos")
        )

    form = ProductoForm()

    if not form.is_submitted():

        form.nombre.data = producto["nombre"]

        form.descripcion.data = producto["descripcion"]

        form.precio.data = producto["precio"]

        form.stock.data = producto["stock"]

    if form.validate_on_submit():

        cursor.execute(
            """
            UPDATE productos
            SET
                nombre = %s,
                descripcion = %s,
                precio = %s,
                stock = %s
            WHERE id = %s
            """,
            (
                form.nombre.data,
                form.descripcion.data,
                float(form.precio.data),
                form.stock.data,
                id
            )
        )

        conn.commit()

        cursor.close()
        conn.close()

        flash(
            "Producto actualizado correctamente.",
            "success"
        )

        return redirect(
            url_for("productos")
        )

    cursor.close()
    conn.close()

    return render_template(
        "formulario_producto.html",
        form=form,
        producto=producto,
        modo="editar"
    )


# ==========================================================
# PRODUCTOS - ELIMINAR
# ==========================================================

@app.route(
    "/productos/eliminar/<int:id>",
    methods=["POST"]
)
@login_required
def eliminar_producto(id):

    conn = obtener_conexion()

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM productos
        WHERE id = %s
        """,
        (id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    flash(
        "Producto eliminado correctamente.",
        "success"
    )

    return redirect(
        url_for("productos")
    )


# ==========================================================
# CLIENTES - LISTAR Y REGISTRAR
# ==========================================================

@app.route(
    "/clientes",
    methods=["GET", "POST"]
)
@login_required
def clientes():

    form = ClienteForm()

    conn = obtener_conexion()

    cursor = conn.cursor(
        cursor_factory=RealDictCursor
    )

    if form.validate_on_submit():

        cursor.execute(
            """
            INSERT INTO clientes
            (
                nombre,
                telefono,
                correo
            )
            VALUES (%s, %s, %s)
            """,
            (
                form.nombre.data,
                form.telefono.data,
                form.email.data
            )
        )

        conn.commit()

        cursor.close()
        conn.close()

        flash(
            "Cliente registrado correctamente.",
            "success"
        )

        return redirect(
            url_for("clientes")
        )

    cursor.execute(
        """
        SELECT
            id_cliente,
            nombre,
            cedula,
            telefono,
            correo
        FROM clientes
        ORDER BY id_cliente DESC
        """
    )

    clientes_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "clientes.html",
        clientes=clientes_data,
        form=form
    )


# ==========================================================
# CLIENTES - MODIFICAR
# ==========================================================

@app.route(
    "/clientes/editar/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def editar_cliente(id):

    conn = obtener_conexion()

    cursor = conn.cursor(
        cursor_factory=RealDictCursor
    )

    cursor.execute(
        """
        SELECT
            id_cliente,
            nombre,
            cedula,
            telefono,
            correo
        FROM clientes
        WHERE id_cliente = %s
        """,
        (id,)
    )

    cliente = cursor.fetchone()

    if cliente is None:

        cursor.close()
        conn.close()

        return redirect(
            url_for("clientes")
        )

    form = ClienteForm()

    if not form.is_submitted():

        form.nombre.data = cliente["nombre"]

        form.email.data = cliente["correo"]

        form.telefono.data = cliente["telefono"]

        form.direccion.data = ""

    if form.validate_on_submit():

        cursor.execute(
            """
            UPDATE clientes
            SET
                nombre = %s,
                telefono = %s,
                correo = %s
            WHERE id_cliente = %s
            """,
            (
                form.nombre.data,
                form.telefono.data,
                form.email.data,
                id
            )
        )

        conn.commit()

        cursor.close()
        conn.close()

        flash(
            "Cliente actualizado correctamente.",
            "success"
        )

        return redirect(
            url_for("clientes")
        )

    cursor.close()
    conn.close()

    return render_template(
        "clientes.html",
        clientes=[cliente],
        form=form,
        modo="editar",
        cliente_editando=cliente
    )


# ==========================================================
# CLIENTES - ELIMINAR
# ==========================================================

@app.route(
    "/clientes/eliminar/<int:id>",
    methods=["POST"]
)
@login_required
def eliminar_cliente(id):

    conn = obtener_conexion()

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM clientes
            WHERE id_cliente = %s
            """,
            (id,)
        )

        conn.commit()

        flash(
            "Cliente eliminado correctamente.",
            "success"
        )

    except IntegrityError:

        conn.rollback()

        flash(
            "No se puede eliminar este cliente porque "
            "está relacionado con una o más facturas.",
            "danger"
        )

    finally:

        cursor.close()
        conn.close()

    return redirect(
        url_for("clientes")
    )


# ==========================================================
# PROVEEDORES - REGISTRAR Y LISTAR
# ==========================================================

@app.route(
    "/proveedores",
    methods=["GET", "POST"]
)
@login_required
def proveedores():

    form = ProveedorForm()

    conn = obtener_conexion()

    cursor = conn.cursor(
        cursor_factory=RealDictCursor
    )

    if form.validate_on_submit():

        cursor.execute(
            """
            INSERT INTO proveedores
            (
                nombre,
                telefono,
                correo
            )
            VALUES (%s, %s, %s)
            """,
            (
                form.nombre.data,
                form.telefono.data,
                form.email.data
            )
        )

        conn.commit()

        cursor.close()
        conn.close()

        flash(
            "Proveedor registrado correctamente.",
            "success"
        )

        return redirect(
            url_for("proveedores")
        )

    cursor.execute(
        """
        SELECT
            id_proveedor,
            nombre,
            telefono,
            correo
        FROM proveedores
        ORDER BY id_proveedor DESC
        """
    )

    proveedores_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "proveedores.html",
        form=form,
        proveedores=proveedores_data
    )


# ==========================================================
# PROVEEDORES - MODIFICAR
# ==========================================================

@app.route(
    "/proveedores/editar/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def editar_proveedor(id):

    conn = obtener_conexion()

    cursor = conn.cursor(
        cursor_factory=RealDictCursor
    )

    cursor.execute(
        """
        SELECT
            id_proveedor,
            nombre,
            telefono,
            correo
        FROM proveedores
        WHERE id_proveedor = %s
        """,
        (id,)
    )

    proveedor = cursor.fetchone()

    if proveedor is None:

        cursor.close()
        conn.close()

        return redirect(
            url_for("proveedores")
        )

    form = ProveedorForm()

    if not form.is_submitted():

        form.nombre.data = proveedor["nombre"]

        form.email.data = proveedor["correo"]

        form.telefono.data = proveedor["telefono"]

        form.direccion.data = ""

    if form.validate_on_submit():

        cursor.execute(
            """
            UPDATE proveedores
            SET
                nombre = %s,
                telefono = %s,
                correo = %s
            WHERE id_proveedor = %s
            """,
            (
                form.nombre.data,
                form.telefono.data,
                form.email.data,
                id
            )
        )

        conn.commit()

        cursor.close()
        conn.close()

        flash(
            "Proveedor actualizado correctamente.",
            "success"
        )

        return redirect(
            url_for("proveedores")
        )

    cursor.close()
    conn.close()

    return render_template(
        "proveedores.html",
        form=form,
        proveedores=[proveedor],
        modo="editar",
        proveedor_editando=proveedor
    )


# ==========================================================
# PROVEEDORES - ELIMINAR
# ==========================================================

@app.route(
    "/proveedores/eliminar/<int:id>",
    methods=["POST"]
)
@login_required
def eliminar_proveedor(id):

    conn = obtener_conexion()

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM proveedores
            WHERE id_proveedor = %s
            """,
            (id,)
        )

        conn.commit()

        flash(
            "Proveedor eliminado correctamente.",
            "success"
        )

    except IntegrityError:

        conn.rollback()

        flash(
            "No se puede eliminar este proveedor porque "
            "está relacionado con uno o más productos.",
            "danger"
        )

    finally:

        cursor.close()
        conn.close()

    return redirect(
        url_for("proveedores")
    )


# ==========================================================
# FACTURACIÓN - REGISTRAR Y LISTAR
# ==========================================================

@app.route(
    "/facturacion",
    methods=["GET", "POST"]
)
@login_required
def facturacion():

    form = FacturacionForm()

    conn = obtener_conexion()

    cursor = conn.cursor(
        cursor_factory=RealDictCursor
    )

    if form.validate_on_submit():

        # Buscar el cliente por su nombre
        cursor.execute(
            """
            SELECT id_cliente
            FROM clientes
            WHERE nombre = %s
            LIMIT 1
            """,
            (form.cliente.data,)
        )

        cliente = cursor.fetchone()

        if cliente is None:

            cursor.close()
            conn.close()

            flash(
                "El cliente ingresado no existe. "
                "Registre primero al cliente.",
                "danger"
            )

            return redirect(
                url_for("facturacion")
            )

        cantidad = int(form.cantidad.data)

        precio = form.precio.data

        total = cantidad * precio

        cursor.execute(
            """
            INSERT INTO facturas
            (
                id_cliente,
                fecha,
                total,
                producto,
                cantidad,
                precio
            )
            VALUES (
                %s,
                CURRENT_DATE,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                cliente["id_cliente"],
                total,
                form.producto.data,
                cantidad,
                precio
            )
        )

        conn.commit()

        cursor.close()
        conn.close()

        flash(
            "Factura registrada correctamente.",
            "success"
        )

        return redirect(
            url_for("facturacion")
        )

    cursor.execute(
        """
        SELECT
            f.id_factura,
            f.id_cliente,
            c.nombre AS cliente_nombre,
            f.fecha,
            f.producto,
            f.cantidad,
            f.precio,
            f.total
        FROM facturas f
        INNER JOIN clientes c
            ON f.id_cliente = c.id_cliente
        ORDER BY f.id_factura DESC
        """
    )

    facturas_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "facturacion.html",
        form=form,
        facturas=facturas_data
    )


# ==========================================================
# FACTURACIÓN - MODIFICAR
# ==========================================================

@app.route(
    "/facturacion/editar/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def editar_factura(id):

    conn = obtener_conexion()

    cursor = conn.cursor(
        cursor_factory=RealDictCursor
    )

    cursor.execute(
        """
        SELECT
            f.id_factura,
            f.id_cliente,
            c.nombre AS cliente_nombre,
            f.fecha,
            f.producto,
            f.cantidad,
            f.precio,
            f.total
        FROM facturas f
        INNER JOIN clientes c
            ON f.id_cliente = c.id_cliente
        WHERE f.id_factura = %s
        """,
        (id,)
    )

    factura = cursor.fetchone()

    if factura is None:

        cursor.close()
        conn.close()

        flash(
            "La factura no existe.",
            "danger"
        )

        return redirect(
            url_for("facturacion")
        )

    form = FacturacionForm()

    if not form.is_submitted():

        form.cliente.data = factura["cliente_nombre"]

        form.producto.data = factura["producto"]

        form.cantidad.data = factura["cantidad"]

        form.precio.data = factura["precio"]

    if form.validate_on_submit():

        cursor.execute(
            """
            SELECT id_cliente
            FROM clientes
            WHERE nombre = %s
            LIMIT 1
            """,
            (form.cliente.data,)
        )

        cliente = cursor.fetchone()

        if cliente is None:

            cursor.close()
            conn.close()

            flash(
                "El cliente ingresado no existe.",
                "danger"
            )

            return render_template(
                "facturacion.html",
                form=form,
                facturas=[factura],
                modo="editar"
            )

        cantidad = int(form.cantidad.data)

        precio = form.precio.data

        total = cantidad * precio

        cursor.execute(
            """
            UPDATE facturas
            SET
                id_cliente = %s,
                producto = %s,
                cantidad = %s,
                precio = %s,
                total = %s
            WHERE id_factura = %s
            """,
            (
                cliente["id_cliente"],
                form.producto.data,
                cantidad,
                precio,
                total,
                id
            )
        )

        conn.commit()

        cursor.close()
        conn.close()

        flash(
            "Factura actualizada correctamente.",
            "success"
        )

        return redirect(
            url_for("facturacion")
        )

    cursor.close()
    conn.close()

    return render_template(
        "facturacion.html",
        form=form,
        facturas=[factura],
        modo="editar"
    )


# ==========================================================
# FACTURACIÓN - ELIMINAR
# ==========================================================

@app.route(
    "/facturacion/eliminar/<int:id>",
    methods=["POST"]
)
@login_required
def eliminar_factura(id):

    conn = obtener_conexion()

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM facturas
            WHERE id_factura = %s
            """,
            (id,)
        )

        conn.commit()

        flash(
            "Factura eliminada correctamente.",
            "success"
        )

    except IntegrityError:

        conn.rollback()

        flash(
            "No se puede eliminar la factura.",
            "danger"
        )

    finally:

        cursor.close()
        conn.close()

    return redirect(
        url_for("facturacion")
    )


# ==========================================================
# EJECUTAR APLICACIÓN
# ==========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )