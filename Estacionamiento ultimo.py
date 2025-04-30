from machine import Pin, PWM, SPI, I2C
from mfrc522 import MFRC522
import time
import ssd1306
import framebuf
import network
from umqtt.simple import MQTTClient
import machine

# --- Configuración WiFi y MQTT ---
WIFI_SSID = "UTNG_GUEST"
WIFI_PASSWORD = "R3d1nv1t4d0s#UT"
MQTT_BROKER = "broker.emqx.io"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "ESP32_Parking"
MQTT_TOPIC = b"abriracceso/barra"
MQTT_STATUS_TOPIC = b"parking/status"
MQTT_PORT = 1883

# --- Conectar a WiFi ---
def conectar_wifi():
    print("Conectando a WiFi", end="")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            print(".", end="")
            time.sleep(0.3)
    print("\nWiFi conectada!")
    print("Dirección IP:", wlan.ifconfig()[0])

# --- Configuración de hardware ---
spi = SPI(1, baudrate=1000000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(23), miso=Pin(19))
rdr = MFRC522(spi=spi, gpio_rst=Pin(4), gpio_cs=Pin(5))

buzzer = PWM(Pin(2))
buzzer.duty(0)

servo_salida = PWM(Pin(33), freq=50)
servo_entrada = PWM(Pin(16), freq=50)

sensor_ir = Pin(25, Pin.IN)

led_rojo = Pin(12, Pin.OUT)
led_amarillo = Pin(13, Pin.OUT)
led_verde = Pin(14, Pin.OUT)

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# --- Funciones útiles ---
def beep(frequency=2000, duration=0.2):
    buzzer.freq(frequency)
    buzzer.duty(512)
    time.sleep(duration)
    buzzer.duty(0)

def mover_servo_tiempo(servo, angulo_inicial, angulo_final, tiempo_total):
    min_duty = 26
    max_duty = 128
    pasos = 50
    tiempo_paso = tiempo_total / pasos
    duty_inicial = int((angulo_inicial / 180) * (max_duty - min_duty) + min_duty)
    duty_final = int((angulo_final / 180) * (max_duty - min_duty) + min_duty)
    paso_duty = (duty_final - duty_inicial) / pasos

    for i in range(pasos + 1):
        duty = int(duty_inicial + i * paso_duty)
        servo.duty(duty)
        time.sleep(tiempo_paso)

def mostrar_texto_invertido_centrado(lines):
    buffer = bytearray(128 * 64 // 8)
    fb = framebuf.FrameBuffer(buffer, 128, 64, framebuf.MONO_VLSB)
    fb.fill(0)
    fb.rect(0, 0, 128, 64, 1)
    for i, line in enumerate(lines):
        x = (128 - len(line)*8) // 2
        y = 14 + i * 10
        fb.text(line, x, y)
    rotated = bytearray(128 * 64 // 8)
    fb_rotated = framebuf.FrameBuffer(rotated, 128, 64, framebuf.MONO_VLSB)
    for x in range(128):
        for y in range(64):
            fb_rotated.pixel(127 - x, 63 - y, fb.pixel(x, y))
    oled.blit(fb_rotated, 0, 0)
    oled.show()

def mensaje_bonito_bienvenida():
    mensaje = ["BIENVENIDO", "Escanee su", "TARJETA RFID"]
    for i in range(1, len(mensaje)+1):
        mostrar_texto_invertido_centrado(mensaje[:i])
        time.sleep(0.5)

def mostrar_uid_en_oled(uid):
    mostrar_texto_invertido_centrado(["TARJETA OK", "UID:", uid])

def mostrar_mensaje_oled(lineas):
    mostrar_texto_invertido_centrado(lineas)

# --- Enviar estado al servidor ---
def enviar_estado(mqtt_client, mensaje):
    try:
        mqtt_client.publish(MQTT_STATUS_TOPIC, mensaje)
        print(f"Estado enviado: {mensaje}")
    except Exception as e:
        print(f"Error al enviar estado: {e}")

# --- Callback MQTT ---
def llegada_mensaje(topic, msg):
    print("[MQTT] Mensaje recibido en", topic, ":", msg)
    topic_str = topic.decode('utf-8') if isinstance(topic, bytes) else topic
    msg_str = msg.decode('utf-8') if isinstance(msg, bytes) else msg

    if topic_str == MQTT_TOPIC.decode('utf-8'):
        comando = msg_str.lower()

        if "subir_entrada" in comando:
            print("Subiendo barrera de entrada")
            try:
                mostrar_mensaje_oled(["ABRIENDO", "ENTRADA"])
                led_amarillo.on()
                led_rojo.off()
                enviar_estado(mqtt_client, "Subiendo barrera entrada")
                mover_servo_tiempo(servo_entrada, 0, 110, 2.5)
                enviar_estado(mqtt_client, "Barrera entrada subida")
            except Exception as e:
                print("Error al subir barrera entrada:", e)
                enviar_estado(mqtt_client, f"Error: {e}")

        elif "bajar_entrada" in comando:
            print("Bajando barrera de entrada")
            try:
                mostrar_mensaje_oled(["CERRANDO", "ENTRADA"])
                mover_servo_tiempo(servo_entrada, 110, 0, 2.5)
                led_amarillo.off()
                led_rojo.on()
                enviar_estado(mqtt_client, "Barrera entrada bajada")
                mensaje_bonito_bienvenida()
            except Exception as e:
                print("Error al bajar barrera entrada:", e)
                enviar_estado(mqtt_client, f"Error: {e}")

        elif "subir_salida" in comando:
            print("Subiendo barrera de salida")
            try:
                mostrar_mensaje_oled(["ABRIENDO", "SALIDA"])
                led_verde.on()
                led_rojo.off()
                enviar_estado(mqtt_client, "Subiendo barrera salida")
                mover_servo_tiempo(servo_salida, 0, 90, 2.5)
                enviar_estado(mqtt_client, "Barrera salida subida")
            except Exception as e:
                print("Error al subir barrera salida:", e)
                enviar_estado(mqtt_client, f"Error: {e}")

        elif "bajar_salida" in comando:
            print("Bajando barrera de salida")
            try:
                mostrar_mensaje_oled(["CERRANDO", "SALIDA"])
                mover_servo_tiempo(servo_salida, 90, 0, 2.5)
                led_verde.off()
                led_rojo.on()
                enviar_estado(mqtt_client, "Barrera salida bajada")
                mensaje_bonito_bienvenida()
            except Exception as e:
                print("Error al bajar barrera salida:", e)
                enviar_estado(mqtt_client, f"Error: {e}")

# --- Conectar y suscribirse al broker MQTT ---
def conectar_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD)
        client.set_callback(llegada_mensaje)
        client.connect()
        client.subscribe(MQTT_TOPIC)
        print("Conectado a MQTT en %s, tópico: %s" % (MQTT_BROKER, MQTT_TOPIC))
        return client
    except Exception as e:
        print("Error al conectar a MQTT:", e)
        return None

# --- Manejo de reconexión ---
def reconectar():
    print("Reconectando...")
    time.sleep(5)
    machine.reset()

# --- Inicio del programa ---
try:
    conectar_wifi()
    mensaje_bonito_bienvenida()
    led_rojo.on()
    led_amarillo.off()
    led_verde.off()

    tiempo_ultimo_detectado = None
    barrera_salida_abierta = False

    mqtt_client = conectar_mqtt()
    if not mqtt_client:
        print("No se pudo conectar a MQTT, reiniciando...")
        reconectar()

    enviar_estado(mqtt_client, "Sistema iniciado correctamente")

    while True:
        try:
            mqtt_client.check_msg()
        except:
            print("Error en MQTT, intentando reconectar...")
            mqtt_client = conectar_mqtt()
            if not mqtt_client:
                reconectar()

        # --- Control de barrera de salida con sensor IR ---
        if sensor_ir.value() == 0:
            if not barrera_salida_abierta:
                print("Vehículo detectado - Subiendo barrera salida...")
                mostrar_mensaje_oled(["VEHÍCULO", "DETECTADO"])
                mover_servo_tiempo(servo_salida, 0, 90, 2.5)
                led_verde.on()
                led_rojo.off()
                tiempo_ultimo_detectado = time.ticks_ms()
                barrera_salida_abierta = True
                enviar_estado(mqtt_client, "Sensor IR: Vehículo detectado")
        else:
            if barrera_salida_abierta and time.ticks_diff(time.ticks_ms(), tiempo_ultimo_detectado) > 3000:
                print("Vehículo salió - Bajando barrera salida...")
                mostrar_mensaje_oled(["VEHÍCULO", "SALIÓ"])
                mover_servo_tiempo(servo_salida, 90, 0, 2.5)
                led_verde.off()
                led_rojo.on()
                barrera_salida_abierta = False
                enviar_estado(mqtt_client, "Sensor IR: Vehículo salió")
                mensaje_bonito_bienvenida()

        # --- Control de barrera de entrada con RFID ---
        (stat, tag_type) = rdr.request(rdr.REQIDL)
        if stat == rdr.OK:
            (stat, raw_uid) = rdr.anticoll()
            if stat == rdr.OK:
                uid = "".join("{:02X}".format(b) for b in raw_uid)
                print("Tarjeta detectada - UID:", uid)
                enviar_estado(mqtt_client, f"Tarjeta RFID detectada: {uid}")

                led_rojo.off()
                led_amarillo.on()
                mostrar_uid_en_oled(uid)
                beep()
                time.sleep(1)

                # Subir barrera de entrada directamente
                mostrar_mensaje_oled(["ABRIENDO", "ENTRADA"])
                mover_servo_tiempo(servo_entrada, 0, 110, 2.5)
                enviar_estado(mqtt_client, "Barrera entrada subida por RFID")
                time.sleep(3)

                # Bajar barrera de entrada después
                mostrar_mensaje_oled(["CERRANDO", "ENTRADA"])
                mover_servo_tiempo(servo_entrada, 110, 0, 2.5)
                enviar_estado(mqtt_client, "Barrera entrada bajada automáticamente")
                led_amarillo.off()
                led_rojo.on()
                mensaje_bonito_bienvenida()

except Exception as e:
    print("Error general:", e)
    reconectar()
