import serial
import csv
from datetime import datetime

# Configura estos parámetros según tu puerto
PUERTO = 'COM4'          # ⚠️ Cambia esto al puerto de tu ESP32 (ej. /dev/ttyUSB0 en Linux)
BAUDIOS = 115200
ARCHIVO = 'datos_sensores.csv'

# Abrir conexión serie
ser = serial.Serial(PUERTO, BAUDIOS, timeout=1)

# Abrir archivo CSV para guardar
with open(ARCHIVO, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    encabezado_guardado = False

    print("⏳ Esperando datos... (Presiona Ctrl+C para detener)")
    
    try:
        while True:
            linea = ser.readline().decode('utf-8').strip()
            if not linea:
                continue

            # Mostrar en consola
            print(linea)

            # Escribir en archivo
            datos = linea.split(",")

            # Guardar encabezado solo una vez
            if not encabezado_guardado and "MQ3" in datos[0]:
                writer.writerow(datos)
                encabezado_guardado = True
            elif encabezado_guardado:
                writer.writerow(datos)

    except KeyboardInterrupt:
        print("\n✅ Lectura detenida por el usuario.")
    finally:
        ser.close()
