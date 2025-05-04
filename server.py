from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
import sqlite3


app = Flask(__name__)

# Inicializar SQLite
DATABASE = 'sensores.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS datos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha TEXT,
                        hora TEXT,
                        temperatura REAL,
                        presion REAL)''')
    conn.commit()
    conn.close()

# Inicializar la base de datos
init_db()

# Ruta para recibir datos del ESP8266
@app.route('/datos', methods=['POST'])
def recibir_datos():
    try:
        # Leer los datos enviados por el ESP8266
        data = request.get_json()
        print("Datos recibidos:", data)  # Mostrar los datos en la terminal

        # Extraer los datos del JSON
        fecha = data['fecha']
        hora = data['hora']
        temperatura = data['temperatura']
        presion = data['presion']

        # Guardar los datos en SQLite
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO datos (fecha, hora, temperatura, presion) VALUES (?, ?, ?, ?)',
                       (fecha, hora, temperatura, presion))
        conn.commit()
        conn.close()

        return jsonify({"message": "Datos almacenados correctamente"}), 200
    except Exception as e:
        # Manejar errores y mostrarlos en la terminal
        print("Error al insertar en SQLite:", str(e))
        return jsonify({"error": str(e)}), 400

# Ruta para consultar datos en el navegador (HTML)
@app.route('/consultar', methods=['GET'])
def consultar_datos():
    rango_horas = request.args.get('rango', default=72, type=int)  # Captura el parámetro de filtro (72h por defecto)

    # Calcular el límite de tiempo para el filtro
    ahora = datetime.now()
    limite_tiempo = ahora - timedelta(hours=rango_horas)
    fecha_limite = limite_tiempo.strftime("%Y-%m-%d")
    hora_limite = limite_tiempo.strftime("%H:%M:%S")

    # Consultar los datos filtrados por fecha y hora
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT fecha, hora, temperatura, presion 
        FROM datos 
        WHERE (strftime("%Y-%m-%d %H:%M:%S", fecha || " " || hora) >= ?)
        ORDER BY fecha DESC, hora DESC
    ''', (fecha_limite + " " + hora_limite,))
    datos = cursor.fetchall()
    conn.close()

    return render_template('index_desarrollo.html', datos=datos, rango=rango_horas)

@app.route('/calendario', methods=['GET', 'POST'])
def calendario():
    resultado = None
    fecha_seleccionada = None

    if request.method == 'POST':
        fecha_seleccionada = request.form['fecha']
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Obtener temperatura máxima y mínima con hora exacta
        cursor.execute('''
            SELECT MAX(temperatura), hora FROM datos WHERE fecha = ? ORDER BY hora DESC LIMIT 1
        ''', (fecha_seleccionada,))
        temp_max = cursor.fetchone()

        cursor.execute('''
            SELECT MIN(temperatura), hora FROM datos WHERE fecha = ? ORDER BY hora ASC LIMIT 1
        ''', (fecha_seleccionada,))
        temp_min = cursor.fetchone()

        # Obtener presión máxima y mínima con hora exacta
        cursor.execute('''
            SELECT MAX(presion), hora FROM datos WHERE fecha = ? ORDER BY hora DESC LIMIT 1
        ''', (fecha_seleccionada,))
        presion_max = cursor.fetchone()

        cursor.execute('''
            SELECT MIN(presion), hora FROM datos WHERE fecha = ? ORDER BY hora ASC LIMIT 1
        ''', (fecha_seleccionada,))
        presion_min = cursor.fetchone()

        conn.close()

        if temp_max and temp_min and presion_max and presion_min:
            resultado = {
                'fecha': fecha_seleccionada,
                'temp_max': temp_max[0], 'hora_temp_max': temp_max[1],
                'temp_min': temp_min[0], 'hora_temp_min': temp_min[1],
                'presion_max': presion_max[0], 'hora_presion_max': presion_max[1],
                'presion_min': presion_min[0], 'hora_presion_min': presion_min[1]
            }
        else:
            resultado = {"mensaje": "No hay datos para el día seleccionado"}

    return render_template('calendario.html', resultado=resultado)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
