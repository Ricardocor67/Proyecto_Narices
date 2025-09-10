import time
import dht
from machine import Pin, ADC


# Pines para los sensores
MQ3_PIN = 39    # Alcohol
MQ5_PIN = 36    # Metano
MQ7_PIN = 34    # Monóxido de carbono
MQ135_PIN = 2   # Calidad del aire
DHT11_PIN = 23  # Temperatura y Humedad

# Inicialización de sensores MQ
def configurar_sensor(pin):
    adc = ADC(Pin(pin))
    adc.atten(ADC.ATTN_11DB)      # Hasta 3.3V
    adc.width(ADC.WIDTH_12BIT)    # 0-4095
    return adc

mq3 = configurar_sensor(MQ3_PIN)
mq5 = configurar_sensor(MQ5_PIN)
mq7 = configurar_sensor(MQ7_PIN)
mq135 = configurar_sensor(MQ135_PIN)

# Sensor DHT11
sensor_dht = dht.DHT11(Pin(DHT11_PIN))

# Función para leer un sensor MQ y convertir su valor a porcentaje respecto al rango ppm
def leer_sensor_porcentaje(sensor):
    """Convierte la lectura ADC en porcentaje relativo 0-100%"""
    valor = sensor.read()
    if valor <= 0 or valor > 4095:
        return None
    porcentaje = (valor / 4095) * 100
    return porcentaje

# Función para leer DHT11
def leer_dht11():
    try:
        sensor_dht.measure()
        return sensor_dht.temperature(), sensor_dht.humidity()
    except:
        return None, None

# Encabezado CSV
print("MQ3 (Alcohol %),MQ5 (METANO %),MQ7 (CO%),MQ135 (NH3%),Temperatura (°C),Humedad (%)")

# Bucle principal
try:
    while True:
        mq3_val = leer_sensor_porcentaje(mq3)
        mq5_val = leer_sensor_porcentaje(mq5)
        mq7_val = leer_sensor_porcentaje(mq7)
        mq135_val = leer_sensor_porcentaje(mq135)
        temp, hum = leer_dht11()  

        # Verificar si algún sensor está desconectado
        if mq3_val is None:
            raise Exception("❌ Error: MQ-3 no está conectado.")
        if mq5_val is None:
            raise Exception("❌ Error: MQ-5 no está conectado.")
        if mq7_val is None:
            raise Exception("❌ Error: MQ-7 no está conectado.")
        if mq135_val is None:
            raise Exception("❌ Error: MQ-135 no está conectado.")
        if temp is None or hum is None:
            raise Exception("❌ Error: DHT11 no está conectado o falló la lectura.")

        # Formatear salida: usa "NA" si el sensor no está conectado
        fila = [
            f"{mq3_val:.2f}" if mq3_val is not None else " ",
            f"{mq5_val:.2f}" if mq5_val is not None else " ",
            f"{mq7_val:.2f}" if mq7_val is not None else " ",
            f"{mq135_val:.2f}" if mq135_val is not None else " ",
            f"{temp}" if temp is not None else " ",
            f"{hum}" if hum is not None else " "
        ]

        print(",".join(fila))
        time.sleep(3)

except Exception as e:
    print(f"Error en el programa: {e}")
