# Proyecto de Detección de Placas y Reconocimiento de Caracteres (OCR) con YOLOv8 y FastAPI

Este proyecto utiliza dos modelos YOLOv8 para detectar placas de vehículos y realizar el reconocimiento de caracteres (OCR) a partir de un stream de video desde una cámara IP. La aplicación expone un servicio web con FastAPI y envía los resultados de las placas detectadas a través de WebSocket.

## Requisitos

### Instalación de dependencias

Asegúrate de tener Python 3.8+ instalado. Para instalar las dependencias del proyecto, ejecuta el siguiente comando:

```bash
pip install -r requirements.txt

## Bibliotecas necesarias
fastapi: Framework web para la API.
uvicorn: Servidor ASGI para ejecutar la API.
opencv-python: Biblioteca de procesamiento de imágenes.
ultralytics: Implementación de YOLOv8 para la detección de objetos.
torch: Usado por YOLOv8 para el aprendizaje profundo.
numpy: Biblioteca para operaciones numéricas.

## Modelos YOLOv8
Asegúrate de tener los modelos YOLOv8 entrenados y colócalos en la carpeta Models/:

    best.pt: Modelo YOLOv8 para la detección de placas.
    best_OCR.pt: Modelo YOLOv8 para el reconocimiento de caracteres (OCR).
## Uso

# 1. Iniciar la aplicación
Para iniciar la aplicación, ejecuta el siguiente comando en la raíz del proyecto:
```bash
uvicorn main:app --reload

Esto lanzará la API en http://127.0.0.1:8000.

# 2. Captura de video desde una cámara IP
Puedes iniciar la captura de video desde la cámara IP accediendo a la ruta /start-camera/:
```bash
http://127.0.0.1:8000/start-camera/

La aplicación comenzará a procesar los fotogramas para detectar placas y realizar OCR en segundo plano.

# 3. Recibir resultados a través de WebSocket
Para recibir las placas detectadas, puedes conectarte al WebSocket en la ruta /ws/detected-plates:

```bash
const socket = new WebSocket("ws://127.0.0.1:8000/ws/detected-plates");

socket.onmessage = function(event) {
    console.log("Placa detectada:", event.data);
};


Cada vez que se detecta una placa, se enviará al cliente conectado a través de WebSocket.

## Configuración

Configurar la cámara IP
En el archivo main.py, debes ajustar la URL de la cámara IP:
```bash
camera_ip_url = "rtsp://usuario:contraseña@IP_CAMARA:554/cam/realmonitor?channel=1&subtype=0"

Reemplaza usuario, contraseña y IP_CAMARA con los valores correctos de tu configuración.

## Parámetros de detección
    threshold: Umbral de diferencia entre fotogramas para evitar procesar imágenes similares.
    classes_ocr: Lista de caracteres que el modelo OCR puede reconocer.

## Estructura del Proyecto
```bash
.
├── Models/                     # Carpeta donde se almacenan los modelos entrenados
│   ├── best.pt                 # Modelo YOLOv8 para detección de placas
│   ├── best_OCR.pt             # Modelo YOLOv8 para OCR
├── main.py                     # Código principal del proyecto
├── requirements.txt            # Archivo de dependencias
├── README.md                   # Este archivo README

## Licencia
Este proyecto está bajo la Licencia MIT.


Este `README.md` proporciona toda la información necesaria para configurar y ejecutar el proyecto.
