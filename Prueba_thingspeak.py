import time
import dht
import urequests
import network
from machine import Pin, ADC

# CONFIGURA TU RED WIFI
SSID = 'RICARDO'
PASSWORD = 'R03062001'

# CONFIGURA TU API KEY DE THINGSPEAK
API_KEY = 'OB3YNNVJT220K2OS'

# Conexión a Wi-Fi
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando a Wi-Fi...')
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print('Conectado. IP:', wlan.ifconfig()[0])
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

# Función para leer el sensor DHT11
def leer_dht11():
    try:
        sensor_dht.measure()
        temperatura = sensor_dht.temperature()
        humedad = sensor_dht.humidity()
        return temperatura, humedad
    except:
        return None, None

# Enviar datos a ThingSpeak
def enviar_a_thingspeak(mq3, mq7, mq135, temp, hum):
    url = "https://api.thingspeak.com/update"
    datos = {
        "api_key": API_KEY,
        "field1": mq3,
        "field2": mq7,
        "field3": mq135,
        "field4": temp,
        "field5": hum
    }
    try:
        respuesta = urequests.post(url, json=datos)
        print("Respuesta de ThingSpeak:", respuesta.text)
        respuesta.close()
    except Exception as e:
        print("Error al enviar:", e)

# Programa principal
conectar_wifi()

while True:
    print("Leyendo sensores...")
    mq3_val = leer_sensor_ppm(mq3, "mq3")
    mq7_val = leer_sensor_ppm(mq7, "mq7")
    mq135_val = leer_sensor_ppm(mq135, "mq135")
    temp, hum = leer_dht11()

    print("MQ-3:", mq3_val, "MQ-7:", mq7_val, "MQ-135:", mq135_val)
    print("Temp:", temp, "Hum:", hum)

    enviar_a_thingspeak(mq3_val, mq7_val, mq135_val, temp, hum)
    time.sleep(20)  # ThingSpeak recomienda 15s mínimo entre envíos
