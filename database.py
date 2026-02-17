import sqlite3

def crear_base_datos():
    conexion = sqlite3.connect("pedidos.db")
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT NOT NULL,
        direccion TEXT NOT NULL,
        telefono TEXT NOT NULL,
        estado TEXT NOT NULL DEFAULT 'Pendiente',
        fecha_creacion TEXT NOT NULL
                   )
                   """)

    conexion.commit()
    conexion.close()

if __name__ == "__main__":
    crear_base_datos()
