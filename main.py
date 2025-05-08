import time
import dht
from machine import Pin, ADC


# Pines para los sensores
MQ3_PIN = 39    # Alcohol
MQ7_PIN = 34    # Monóxido de carbono
MQ135_PIN = 2   # Calidad del aire
DHT11_PIN = 23  # Temperatura y Humedad

# Inicialización de sensores MQ
def configurar_sensor(pin):
    sensor = ADC(Pin(pin))
    sensor.atten(ADC.ATTN_11DB)        # Hasta 3.3V
    sensor.width(ADC.WIDTH_12BIT)      # 0-4095
    return sensor

mq3 = configurar_sensor(MQ3_PIN)
mq7 = configurar_sensor(MQ7_PIN)
mq135 = configurar_sensor(MQ135_PIN)

# Sensor DHT11
sensor_dht = dht.DHT11(Pin(DHT11_PIN))


# Rango de detección estimado para cada sensor en ppm
rango_ppm = {
    "mq3":  (50, 1000),   # Alcohol
    "mq7":  (20, 2000),    # Monóxido de carbono
    "mq135": (10, 1000)    # Amoniaco u otros gases
}

# Función para leer un sensor MQ y convertir su valor a porcentaje respecto al rango ppm
def leer_sensor_ppm(sensor, nombre):
    valor = sensor.read()
    if valor <= 0 or valor >= 4095                                                                                                                                                  :
        return None  # Lectura inválida

    voltaje = (valor / 4095)*0.1                                                                                                                                                                                       # Conversión ADC -> Voltaje

    min_ppm, max_ppm = rango_ppm[nombre]

    # Estimamos una lectura lineal
    ppm = (voltaje / 5) * (max_ppm - min_ppm) + min_ppm

    porcentaje = ((ppm - min_ppm) / (max_ppm - min_ppm)) * 100
    porcentaje = max(0, min(porcentaje, 100))  # Limitar entre 0 y 100%
    return porcentaje

# Función para leer DHT11
def leer_dht11():
    try:
        sensor_dht.measure()
        return sensor_dht.temperature(), sensor_dht.humidity()
    except:
        return None, None

# Encabezado CSV
print("MQ3 (Alcohol %),MQ7 (CO%),MQ135 (NH3%),Temperatura (°C),Humedad (%)")

# Bucle principal
try:
    while True:
        mq3_val = leer_sensor_ppm(mq3, "mq3")
        mq7_val = leer_sensor_ppm(mq7, "mq7")
        mq135_val = leer_sensor_ppm(mq135, "mq135")
        temp, hum = leer_dht11()
        
        
        # Verificar si algún sensor está desconectado
        if mq3_val is None:
            raise Exception("❌ Error: MQ-3 no está conectado.")
        if mq7_val is None:
            raise Exception("❌ Error: MQ-7 no está conectado.")
        if mq135_val is None:
            raise Exception("❌ Error: MQ-135 no está conectado.")
        if temp is None or hum is None:
            raise Exception("❌ Error: DHT11 no está conectado o falló la lectura.")


        # Formatear salida: usa "NA" si el sensor no está conectado
        fila = [
            f"{mq3_val:.2f}" if mq3_val is not None else " ",
            f"{mq7_val:.2f}" if mq7_val is not None else " ",
            f"{mq135_val:.2f}" if mq135_val is not None else " ",
            f"{temp}" if temp is not None else " ",
            f"{hum}" if hum is not None else " "
        ]

        print(",".join(fila))
        time.sleep(3)

except Exception as e:
    print(f"Error en el programa: {e}")
