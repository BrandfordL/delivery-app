from flask import Flask, render_template, url_for, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

def obtener_conexion():
    conexion = sqlite3.connect("pedidos.db")
    conexion.row_factory = sqlite3.Row
    return conexion

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/pedidos")
def pedidos():
    conexion = obtener_conexion()
    pedidos = conexion.execute("SELECT * FROM pedidos").fetchall()
    conexion.close()

    return render_template("pedidos.html", pedidos=pedidos)

@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template("404.html"), 404

@app.route("/agregar_pedido", methods=["POST"])
def agregar_pedido():
    cliente = request.form["cliente"]
    direccion = request.form["direccion"]
    telefono = request.form["telefono"]

    if not cliente or not direccion or not telefono:
        return "Todos los campos son obligatorios"

    fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conexion = obtener_conexion()
    conexion.execute(
        """
        INSERT INTO pedidos (cliente, direccion, telefono, estado, fecha_creacion)
        VALUES (?, ?, ?, ?, ?)
        """,
        (cliente, direccion, telefono, "Pendiente", fecha_creacion)
    )
    conexion.commit()
    conexion.close()

    return redirect(url_for("pedidos"))

@app.route("/eliminar/<int:id>")
def eliminar_pedido(id):
    conexion = obtener_conexion()
    conexion.execute("DELETE FROM pedidos WHERE id = ?", (id,))
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
    cliente = request.form["cliente"]
    direccion = request.form["direccion"]

    conexion = obtener_conexion()
    conexion.execute(
        "UPDATE pedidos SET cliente = ?, direccion = ? WHERE id = ?",
        (cliente, direccion, id)
    )
    conexion.commit()
    conexion.close()

    return redirect(url_for("pedidos"))

@app.route("/cambiar_estado/<int:id>")
def cambiar_estado(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Obtener estado actual
    cursor.execute("SELECT estado FROM pedidos WHERE id = ?", (id,))
    pedido = cursor.fetchone()

    if pedido is None:
        conexion.close()
        return "Pedido no encontrado"

    estado_actual = pedido["estado"]

    # Lógica de cambio de estado
    if estado_actual == "Pendiente":
        nuevo_estado = "En camino"
    elif estado_actual == "En camino":
        nuevo_estado = "Entregado"
    else:
        nuevo_estado = "Pendiente"

    # Actualizar en base de datos
    cursor.execute(
        "UPDATE pedidos SET estado = ? WHERE id = ?",
        (nuevo_estado, id)
    )

    conexion.commit()
    conexion.close()

    return redirect(url_for("pedidos"))

if __name__ == "__main__":
    app.run(debug=True)
