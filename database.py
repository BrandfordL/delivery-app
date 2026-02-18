import sqlite3
from werkzeug.security import generate_password_hash

def crear_base_datos():
    conexion = sqlite3.connect("pedidos.db")
    cursor = conexion.cursor()

    # Tabla de usuarios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        rol TEXT NOT NULL
    )
    """)

    # Tabla de pedidos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        direccion TEXT NOT NULL,
        telefono TEXT NOT NULL,
        estado TEXT NOT NULL DEFAULT 'Pendiente',
        fecha_creacion TEXT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )
    """)

    # Verificar si existe el domiciliario inicial
    cursor.execute("""
        SELECT * FROM usuarios WHERE nombre = ?
    """, ("domi1",))
    
    usuario = cursor.fetchone()

    if not usuario:
        cursor.execute("""
            INSERT INTO usuarios (nombre, password, rol)
            VALUES (?, ?, ?)
        """, (
            "domi1",
            generate_password_hash("1234"),
            "domiciliario"
        ))

    conexion.commit()
    conexion.close()


if __name__ == "__main__":
    crear_base_datos()
