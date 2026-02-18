from flask import Flask, render_template, url_for, request, redirect, session
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super_secret_key"

def obtener_conexion():
    conexion = sqlite3.connect("pedidos.db")
    conexion.row_factory = sqlite3.Row
    return conexion

@app.route("/")
def home():
    if "usuario_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["username"]
        password = generate_password_hash(request.form["password"])
        rol = "cliente"

        conexion = obtener_conexion()

        usuario_existente = conexion.execute(
            "SELECT * FROM usuarios WHERE nombre = ?",
            (nombre,)
        ).fetchone()

        if usuario_existente:
            conexion.close()
            return "El usuario ya existe"

        conexion.execute(
            "INSERT INTO usuarios (nombre, password, rol) VALUES (?, ?, ?)",
            (nombre, password, rol)
        )

        conexion.commit()
        conexion.close()

        return redirect(url_for("login"))

    return render_template("registro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conexion = obtener_conexion()
        usuario = conexion.execute(
            "SELECT * FROM usuarios WHERE nombre = ?",
            (username,)
        ).fetchone()
        conexion.close()

        if usuario and check_password_hash(usuario["password"], password):
            session["usuario_id"] = usuario["id"]
            session["usuario"] = usuario["nombre"]
            session["rol"] = usuario["rol"]

            return redirect(url_for("dashboard"))

        else:
            error = "Usuario o contraseña incorrectos"

    return render_template("login.html", error=error)

@app.route("/dashboard")
def dashboard():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    if session["rol"] == "cliente":
        return redirect(url_for("dashboard_cliente"))

    elif session["rol"] == "domiciliario":
        return redirect(url_for("dashboard_domiciliario"))

    else:
        return "Rol no válido"

@app.route("/dashboard_cliente")
def dashboard_cliente():
    if "usuario" not in session or session["rol"] != "cliente":
        return redirect(url_for("login"))

    conexion = obtener_conexion()
    pedidos = conexion.execute("""
        SELECT * FROM pedidos
        WHERE usuario_id = ?
        ORDER BY fecha_creacion DESC
    """, (session["usuario_id"],)).fetchall()
    conexion.close()

    return render_template("dashboard_cliente.html", pedidos=pedidos)

@app.route("/dashboard_domiciliario")
def dashboard_domiciliario():
    if "usuario" not in session or session["rol"] != "domiciliario":
        return redirect(url_for("login"))

    conexion = obtener_conexion()
    pedidos = conexion.execute("""
        SELECT * FROM pedidos
        WHERE estado = 'Pendiente'
        ORDER BY fecha_creacion ASC
    """).fetchall()
    conexion.close()

    return render_template("dashboard_domiciliario.html", pedidos=pedidos)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/pedidos")
def pedidos():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexion = obtener_conexion()

    if session["rol"] == "cliente":
        pedidos = conexion.execute("""
            SELECT pedidos.*, usuarios.nombre
            FROM pedidos
            JOIN usuarios ON pedidos.usuario_id = usuarios.id
            WHERE pedidos.usuario_id = ?
        """, (session["usuario_id"],)).fetchall()

    elif session["rol"] == "domiciliario":
        pedidos = conexion.execute("""
            SELECT pedidos.*, usuarios.nombre
            FROM pedidos
            JOIN usuarios ON pedidos.usuario_id = usuarios.id
            WHERE estado != 'Entregado'
        """).fetchall()

    conexion.close()

    return render_template("pedidos.html", pedidos=pedidos)

@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template("404.html"), 404

@app.route("/agregar_pedido", methods=["POST"])
def agregar_pedido():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    direccion = request.form["direccion"]
    telefono = request.form["telefono"]

    if not direccion or not telefono:
        return "Todos los campos son obligatorios"

    fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conexion = obtener_conexion()
    conexion.execute(
        """
        INSERT INTO pedidos (usuario_id, direccion, telefono, estado, fecha_creacion)
        VALUES (?, ?, ?, ?, ?)
        """,
        (session["usuario_id"], direccion, telefono, "Pendiente", fecha_creacion)
    )
    conexion.commit()
    conexion.close()

    return redirect(url_for("pedidos"))

@app.route("/eliminar/<int:id>")
def eliminar_pedido(id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexion = obtener_conexion()

    conexion.execute("""
        DELETE FROM pedidos
        WHERE id = ? AND usuario_id = ?
    """, (id, session["usuario_id"]))

    conexion.commit()
    conexion.close()

    return redirect(url_for("pedidos"))

@app.route("/editar/<int:id>")
def editar_pedido(id):
    conexion = obtener_conexion()
    pedido = conexion.execute(
        "SELECT * FROM pedidos WHERE id = ?",
        (id,)
    ).fetchone()
    conexion.close()

    return render_template("editar.html", pedido=pedido)

@app.route("/actualizar/<int:id>", methods=["POST"])
def actualizar_pedido(id):
    direccion = request.form["direccion"]
    telefono = request.form["telefono"]

    conexion = obtener_conexion()
    conexion.execute(
        "UPDATE pedidos SET direccion = ?, telefono = ? WHERE id = ?",
        (direccion, telefono, id)
    )
    conexion.commit()
    conexion.close()

    return redirect(url_for("pedidos"))

@app.route("/cambiar_estado/<int:pedido_id>")
def cambiar_estado(pedido_id):
    if "usuario" not in session or session["rol"] != "domiciliario":
        return redirect(url_for("login"))

    conexion = obtener_conexion()
    conexion.execute("""
        UPDATE pedidos
        SET estado = 'En camino'
        WHERE id = ?
    """, (pedido_id,))
    conexion.commit()
    conexion.close()

    return redirect(url_for("dashboard_domiciliario"))

@app.route("/entregar_pedido/<int:pedido_id>")
def entregar_pedido(pedido_id):
    if "usuario" not in session or session["rol"] != "domiciliario":
        return redirect(url_for("login"))

    conexion = obtener_conexion()
    conexion.execute("""
        UPDATE pedidos
        SET estado = 'Entregado'
        WHERE id = ?
    """, (pedido_id,))
    conexion.commit()
    conexion.close()

    return redirect(url_for("dashboard_domiciliario"))

if __name__ == "__main__":
    app.run(debug=True)
