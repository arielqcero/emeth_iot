import sqlite3
import matplotlib.pyplot as plt

# Conectar a la base de datos SQLite
DATABASE = 'sensores.db'

def obtener_datos(fecha_inicio, fecha_fin):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Consulta para obtener datos en el rango de fechas
    query = '''SELECT fecha, hora, temperatura, presion 
               FROM datos 
               WHERE fecha BETWEEN ? AND ? 
               ORDER BY fecha, hora'''
    cursor.execute(query, (fecha_inicio, fecha_fin))
    datos = cursor.fetchall()
    conn.close()
    return datos

def graficar_datos(fecha_inicio, fecha_fin):
    # Obtener datos del rango de fechas
    datos = obtener_datos(fecha_inicio, fecha_fin)
    
    # Extraer valores para graficar
    fechas_horas = [f"{fila[0]} {fila[1]}" for fila in datos]
    temperaturas = [fila[2] for fila in datos]
    presiones = [fila[3] for fila in datos]
    
    # Crear el gráfico
    plt.figure(figsize=(10, 6))
    #plt.plot(fechas_horas, temperaturas, label="Temperatura (°C)", color="red")
    plt.plot(fechas_horas, presiones, label="Presión (hPa)", color="blue")
    
    # Configurar el gráfico
    plt.title(f"Temperatura y Presión entre {fecha_inicio} y {fecha_fin}")
    plt.xlabel("Fecha y Hora")
    plt.ylabel("Valores")
    plt.xticks(rotation=45, fontsize=8)
    plt.legend()
    plt.grid()
    plt.tight_layout()
    
    # Mostrar el gráfico
    plt.show()

# Define el rango de fechas
fecha_inicio = "20-4-2025"
fecha_fin = "26-4-2025"

# Llama a la función para graficar
graficar_datos(fecha_inicio, fecha_fin)