import network
import time

wlan = network.WLAN(network.STA_IF)
wlan.active(False)
time.sleep(1)
wlan.active(True)
wlan.connect('RICARDO', 'R03062001')

print("Conectando...")
for _ in range(10):
    if wlan.isconnected():
        print("✅ Conectado con IP:", wlan.ifconfig()[0])
        break
    time.sleep(1)
else:
    print("❌ No se pudo conectar a Wi-Fi")
