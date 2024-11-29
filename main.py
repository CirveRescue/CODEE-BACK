import sqlite3
from fastapi import FastAPI, BackgroundTasks, WebSocket
import cv2
import numpy as np
from pydantic import BaseModel
from ultralytics import YOLO
import asyncio
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta

# Inicializar la aplicación FastAPI
app = FastAPI()

# Cargar los modelos YOLOv8
model_plate = YOLO("Models/best.pt")  # Modelo para detección de placas
model_ocr = YOLO("Models/best_OCR.pt")  # Modelo para OCR

# Clases del modelo OCR
classes_ocr = [
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 
    'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
]

# Almacenar placas detectadas
detected_plates = []

# Función para activar la pluma mediante HTTP
def activar_pluma_via_http(esp32_host, username, password):
    try:
        response = requests.get(
            f"http://{esp32_host}/activar_pluma", 
            auth=HTTPBasicAuth(username, password)
        )
        if response.status_code == 200:
            print(f"Pluma del ESP32 {esp32_host} activada exitosamente.")
        else:
            print(f"Error activando la pluma del ESP32 {esp32_host}. Código de estado: {response.status_code}")
    except Exception as e:
        print(f"Error en la conexión HTTP con {esp32_host}: {e}")

def validar_y_registrar_entrada(placa_detectada, camara_nombre, camara_ubicacion):
    conn = sqlite3.connect('C:\\xampp\\htdocs\\CODEE-FRONT\\database\\CODE.db')
    cursor = conn.cursor()

    # Diccionario para mapear cámaras con ESP32
    camaras_esp32 = {
        # Estructura: "NOMBRE_CAMARA": ("ESP32_HOST", "USERNAME", "PASSWORD")
        "Cámara 1": ("192.168.100.85", "ESP32", "Tamalito26"),  # Entrada 1
        "Cámara 2": ("192.168.0.102", "ESP32", "Tamalito26"),  # Entrada 2
        "Cámara 3": ("192.168.0.103", "ESP32", "Tamalito26"),  # Salida 1
        "Cámara 4": ("192.168.0.104", "ESP32", "Tamalito26"),  # Salida 2
    }

    if camara_nombre not in camaras_esp32:
        print(f"La cámara {camara_nombre} no está configurada en el sistema.")
        return

    esp32_host, username, password = camaras_esp32[camara_nombre]

    # Recuperar el vehículo de la base de datos
    cursor.execute("SELECT * FROM vehiculo WHERE placa = ?", (placa_detectada,))
    vehiculo = cursor.fetchone()

    if vehiculo:
        print(f"La placa {placa_detectada} está registrada en la base de datos.")

        if camara_ubicacion == "Entrada":
            cursor.execute("""
                SELECT * FROM entrada WHERE vehiculo_id = ? AND tipo_movimiento = 'Entrada' 
                AND fecha_movimiento > ?
            """, (vehiculo[0], datetime.now() - timedelta(minutes=10)))

            entrada_reciente = cursor.fetchone()

            if entrada_reciente:
                print(f"El vehículo con placa {placa_detectada} ya tiene una entrada registrada recientemente. No se registrará nuevamente.")
            else:
                # Activar la pluma
                activar_pluma_via_http(esp32_host, username, password)

                # Registrar entrada
                cursor.execute("""
                    INSERT INTO entrada (usuario_id, vehiculo_id, tipo_movimiento, fecha_movimiento, created_at, updated_at)
                    VALUES (?, ?, 'Entrada', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (vehiculo[1], vehiculo[0]))
                conn.commit()
                print(f"Se ha registrado la entrada del vehículo con placa {placa_detectada}.")

        elif camara_ubicacion == "Salida":
            cursor.execute("SELECT * FROM entrada WHERE vehiculo_id = ? AND tipo_movimiento = 'Entrada'", (vehiculo[0],))
            entrada = cursor.fetchone()

            if entrada:
                print(f"El vehículo con placa {placa_detectada} tiene una entrada registrada.")
                
                # Activar la pluma
                activar_pluma_via_http(esp32_host, username, password)

                # Registrar salida
                cursor.execute("""
                    INSERT INTO salida (usuario_id, vehiculo_id, tipo_movimiento, fecha_movimiento, created_at, updated_at)
                    VALUES (?, ?, 'Salida', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (entrada[1], vehiculo[0]))
                conn.commit()
                
                # Eliminar la entrada después de registrar la salida
                cursor.execute("DELETE FROM entrada WHERE id = ?", (entrada[0],))
                conn.commit()

                print(f"Se ha registrado la salida del vehículo con placa {placa_detectada} y se ha eliminado la entrada.")
            else:
                print(f"El vehículo con placa {placa_detectada} no tiene una entrada registrada para salir.")
    else:
        print(f"El vehículo con placa {placa_detectada} no se encuentra registrado en la base de datos.")

    conn.close()



# Obtener las URLs de las cámaras desde la base de datos
def obtener_camaras_desde_bd():
    conn = sqlite3.connect('C:\\xampp\\htdocs\\CODEE-FRONT\\database\\CODE.db')
    cursor = conn.cursor()

    # Recuperar ID, URL, ubicación y estado de las cámaras activas
    cursor.execute("""
        SELECT Tipo_Dispositivo, IP_Camara, Ubicacion 
        FROM dispositivo
        WHERE Estado_Dispositivo = 'Activo'
    """)
    camaras = cursor.fetchall()
    conn.close()

    return [{"id": camara[0], "url": camara[1], "ubicacion": camara[2]} for camara in camaras]



# Procesar un fotograma
def process_frame(frame, camara_id, camara_ubicacion):
    results_plate = model_plate(frame)
    plates_detected = []

    for result in results_plate:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            plate_img = frame[y1:y2, x1:x2]

            if plate_img.size == 0:
                continue

            results_ocr = model_ocr(plate_img)
            detected_chars = []

            for result_ocr in results_ocr:
                boxes_ocr = result_ocr.boxes
                for box_ocr in boxes_ocr:
                    cls = int(box_ocr.cls[0])
                    character = classes_ocr[cls]
                    x1_char = int(box_ocr.xyxy[0][0])
                    detected_chars.append((x1_char, character))

            detected_chars = sorted(detected_chars, key=lambda x: x[0])
            plate_text = ''.join([char for _, char in detected_chars])

            if plate_text.strip():
                plates_detected.append({
                    "plate_text": plate_text.strip(),
                    "coordinates": [x1, y1, x2, y2],
                    "camara_id": camara_id,
                    "ubicacion": camara_ubicacion
                })
                detected_plates.append({
                    "plate_text": plate_text.strip(),
                    "camara_id": camara_id,
                    "ubicacion": camara_ubicacion
                })
                validar_y_registrar_entrada(plate_text.strip(), camara_id, camara_ubicacion)

    return {"plates_detected": plates_detected}


# Capturar y procesar video desde varias cámaras
async def capturar_desde_camaras():
    camaras = obtener_camaras_desde_bd()

    while True:
        for camara in camaras:
            camara_id = camara["id"]
            camara_url = camara["url"]
            camara_ubicacion = camara["ubicacion"]

            cap = cv2.VideoCapture(camara_url)
            if not cap.isOpened():
                print(f"Error al abrir la cámara {camara_id} ({camara_ubicacion})")
                continue

            ret, frame = cap.read()
            if ret:
                result = process_frame(frame, camara_id, camara_ubicacion)
                result["camara_id"] = camara_id
                result["ubicacion"] = camara_ubicacion  # Añadir la ubicación a los resultados
                print(f"Resultados para cámara {camara_id} ({camara_ubicacion}): {result}")

            cap.release()

        await asyncio.sleep(1)  # Esperar un segundo antes de procesar de nuevo


connected_clients = set()  # Lista de clientes conectados

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            await asyncio.sleep(1)  # Mantener la conexión abierta
    except:
        connected_clients.remove(websocket)

def enviar(mensaje):
    for client in connected_clients:
        asyncio.create_task(client.send_text(mensaje))

# Iniciar el procesamiento de cámaras
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(capturar_desde_camaras())


class PlacaInput(BaseModel):
    placa: str  # La clave debe coincidir exactamente con lo que se envía


@app.post("/api/manual-entry")
async def manual_entry(input: PlacaInput):
    """
    Endpoint para recibir placas manuales desde Laravel
    """
    print(f"Placa recibida manualmente: {input.placa}")

    # Procesar la lógica de registro o autorización de la placa
    validar_y_registrar_entrada(input.placa, "Cámara 2", "Salida")

    return {"message": f"Placa {input.placa} procesada exitosamente."}

# Ejecución del servidor
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
