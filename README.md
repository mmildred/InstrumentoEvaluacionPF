# 🚗 SISTEMA DE ESTACIONAMIENTO INTELIGENTE 🅿️  
**UNIDAD 3: INSTRUMENTO DE EVALUACIÓN - PROYECTO FINAL**  

---

## 🌟 Descripción General  
Sistema automatizado de control de acceso para estacionamientos que combina:  
- Identificación por **RFID** para entrada  
- Detección por **sensor infrarrojo** para salida  
- Comunicación **MQTT** para monitoreo remoto  
- Visualización en **pantalla OLED**  
- Indicadores luminosos (**LEDs**) y sonoros (**buzzer**)  

---

## 🛠️ Componentes y Especificaciones Técnicas  

### 🔌 Hardware  
| Componente | Especificaciones | Función |
|------------|------------------|---------|
| **ESP32** | Microcontrolador dual-core | Cerebro del sistema |
| **Módulo RFID RC522** | Frecuencia 13.56MHz | Lectura de tarjetas |
| **Servomotores SG90** | 180° de rotación | Control de barreras |
| **Sensor IR** | HL-69 | Detección de vehículos |
| **Pantalla OLED SSD1306** | 128x64 píxeles | Visualización |
| **LEDs (RGB)** | Rojo/Verde/Amarillo | Indicación de estado |
| **Buzzer pasivo** | 5V | Señales audibles |

### 💻 Software  
- **MicroPython 1.19.1**  
- **Node-RED 3.0+** (para dashboard)  
- **Protocolo MQTT 3.1.1**  
- **Librerías**:  
  - `mfrc522` (para RFID)  
  - `ssd1306` (para pantalla OLED)  
  - `umqtt.simple` (para MQTT)  

---

## 📋 Código Principal [![MicroPython](https://img.shields.io/badge/VER_CÓDIGO-007ACC?style=for-the-badge&logo=python&logoColor=white)](https://github.com/mmildred/InstrumentoEvaluacionPF/blob/main/Estacionamiento%20ultimo.py)

# Configuración WiFi
WIFI_SSID = "UTNG_GUEST"
WIFI_PASSWORD = "R3d1nv1t4d0s#UT"

# Configuración MQTT
MQTT_BROKER = "broker.emqx.io"
MQTT_TOPIC = b"abriracceso/barra"

# Inicialización hardware
spi = SPI(1, baudrate=1000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
rdr = MFRC522(spi=spi, gpio_rst=Pin(4), gpio_cs=Pin(5))
servo_entrada = PWM(Pin(16), freq=50)
sensor_ir = Pin(25, Pin.IN)

### 🔌 Circuito Electrónico  
![Diagrama del Circuito](https://github.com/user-attachments/assets/387c865f-036d-4424-bfa2-7e359e50f133)  
*Diagrama de conexiones del sistema*  

### 🌐 Flujo Node-RED  
[![Node-RED](https://img.shields.io/badge/Node--RED-Flujo_JSON-green)](https://github.com/mmildred/InstrumentoEvaluacionPF/blob/main/node-red3-json.json)  
![Interfaz Node-RED](https://github.com/user-attachments/assets/4ab97f2b-2ee3-400d-874a-9cd62059870d)  

---

## 🚀 Conexión  
| 1 | 2 |
|--------|--------|
| ![1](https://github.com/user-attachments/assets/f27e8406-b91e-43fd-8db0-af1ca7f5d652) | ![2](https://github.com/user-attachments/assets/ce514bb5-6052-41e7-b624-0ec580175430) |

---

## 🎯 Producto Final  
| 1 | 2 |
|--------|--------|
| ![1](https://github.com/user-attachments/assets/0952cb4f-dd87-4d99-9b33-690113abc367) | ![2](https://github.com/user-attachments/assets/4cb75d20-bae3-4ad7-b18d-b871864f1643) |

---

## ▶️ Video Demostración  
[![Video Demo](https://img.shields.io/badge/🎥-Ver_Video_Demo-red)](https://drive.google.com/file/d/1IkWIEEnOwtfyAgufyPPKngzTXMUnKYyu/view?usp=sharing)  

---

## 📌 Notas  
- Desarrollado como parte de la evaluación de la Unidad 3  
- Integra hardware (sensores) y software (MicroPython + Node-RED)  
2b-2ee3-400d-874a-9cd62059870d)
