import serial
import csv
import time
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# === CONFIGURACIÓN DEL PUERTO SERIAL ===
PORT = "COM4"        # Puerto del ESP32
BAUDRATE = 115200    # Velocidad de comunicación
ARCHIVO = "lecturas_sensores.csv"

# === ABRIR PUERTO SERIAL ===
ser = serial.Serial(PORT, BAUDRATE, timeout=1)
print(f"📡 Conectado a {PORT} ({BAUDRATE} baudios)\n")

# === CONFIGURAR CSV ===
header_guardado = False
datos = []

# === CONFIGURAR GRAFICAS EN TIEMPO REAL ===
plt.ion()  # Modo interactivo
fig, axs = plt.subplots(3, 1, figsize=(12, 12))
fig.suptitle("Lecturas en Tiempo Real (ESP32)")

# Etiquetas de los gráficos
axs[0].set_title("Gases")
axs[0].set_ylabel("Concentración (%)")
axs[1].set_title("Temperatura")
axs[1].set_ylabel("°C")
axs[2].set_title("Humedad")
axs[2].set_ylabel("% Humedad")
for ax in axs:
    ax.set_xlabel("Tiempo")
    ax.grid(True)

# === LECTURA Y GRAFICA EN TIEMPO REAL ===
try:
    while True:
        linea = ser.readline().decode(errors="ignore").strip()
        if not linea:
            continue

        print(f"➡ {linea}")

        # Guardar encabezado
        if not header_guardado and "MQ3" in linea:
            header = ["Tiempo"] + [col.strip() for col in linea.split(",")]
            header_guardado = True
            continue

        # Guardar datos
        if header_guardado:
            try:
                valores = [float(x.strip()) for x in linea.split(",")]
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                datos.append([timestamp] + valores)

                # Convertir a DataFrame para graficar
                df = pd.DataFrame(datos, columns=header)
                df['Tiempo'] = pd.to_datetime(df['Tiempo'])

                # Limpiar gráficos anteriores
                for ax in axs:
                    ax.cla()
                
                # Graficar Gases
                axs[0].plot(df['Tiempo'], df['MQ3 (Alcohol %)'], label='MQ3 (Alcohol)', marker='o')
                axs[0].plot(df['Tiempo'], df['MQ5 (METANO %)'], label='MQ5 (Metano)', marker='o')
                axs[0].plot(df['Tiempo'], df['MQ7 (CO%)'], label='MQ7 (CO)', marker='o')
                axs[0].plot(df['Tiempo'], df['MQ135 (NH3%)'], label='MQ135 (NH3)', marker='o')
                axs[0].set_title("Gases")
                axs[0].set_ylabel("Concentración (%)")
                axs[0].legend()
                axs[0].grid(True)

                # Graficar Temperatura
                axs[1].plot(df['Tiempo'], df['Temperatura (°C)'], color='red', label='Temperatura', marker='o')
                axs[1].set_title("Temperatura")
                axs[1].set_ylabel("°C")
                axs[1].legend()
                axs[1].grid(True)

                # Graficar Humedad
                axs[2].plot(df['Tiempo'], df['Humedad (%)'], color='blue', label='Humedad', marker='o')
                axs[2].set_title("Humedad")
                axs[2].set_ylabel("% Humedad")
                axs[2].legend()
                axs[2].grid(True)

                # Actualizar gráficos
                plt.tight_layout()
                plt.pause(0.1)

            except ValueError:
                continue

except KeyboardInterrupt:
    print("\n⏹ Lectura detenida por el usuario.")

finally:
    ser.close()
    print("✅ Puerto serial cerrado.")

    # Guardar CSV final
    if datos:
        with open(ARCHIVO, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(datos)
        print(f"💾 Datos guardados en: {ARCHIVO}")
