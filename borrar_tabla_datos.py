import sqlite3

DATABASE = 'sensores.db'

def limpiar_tabla():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM datos')  # Borra todos los registros de la tabla
    conn.commit()
    conn.close()
    print("Tabla datos limpiada correctamente.")

# Ejecuta la función para borrar los datos
limpiar_tabla()