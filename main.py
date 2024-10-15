import sqlite3
from fastapi import FastAPI, BackgroundTasks, WebSocket
import cv2
import numpy as np
from ultralytics import YOLO
import asyncio

# Inicializar la aplicación FastAPI
app = FastAPI()

# Cargar los modelos YOLOv8
model_plate = YOLO("Models/best.pt")  # Ruta al archivo del modelo entrenado para detección de placas
model_ocr = YOLO("Models/best_OCR.pt")  # Ruta al archivo del modelo entrenado para OCR

# URL de la cámara IP (ajústala según tu configuración)
camera_ip_url = "rtsp://888888:888888@192.168.1.10:554/cam/realmonitor?channel=2&subtype=0"

# Clases de caracteres que el modelo OCR puede detectar
classes_ocr = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 
               'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

# Almacenar placas detectadas
detected_plates = []

# Conectar a la base de datos
def validar_y_registrar_entrada(placa_detectada):
    conn = sqlite3.connect('C:\xampp\htdocs\codee\database\CODEE.db')  # Cambia por el nombre de tu base de datos
    cursor = conn.cursor()

    # Verificar si la placa ya existe en la base de datos
    cursor.execute("SELECT * FROM vehiculos WHERE placa = ?", (placa_detectada,))
    vehiculo = cursor.fetchone()

    if vehiculo:
        print(f"La placa {placa_detectada} ya está registrada en la base de datos.")
        # Aquí puedes actualizar la hora de entrada o realizar alguna acción.
    else:
        print(f"La placa {placa_detectada} no está registrada. Registrando nueva entrada...")
        # Registrar la nueva entrada
        cursor.execute("INSERT INTO entradas (vehiculo_id, fecha_entrada) VALUES (?, datetime('now'))", (vehiculo_id,))
        conn.commit()

    conn.close()

@app.websocket("/ws/detected-plates")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    while True:
        if detected_plates:
            # Enviar la placa detectada al cliente
            plate_text = detected_plates.pop(0)  # Obtiene y elimina la primera placa
            await websocket.send_text(plate_text)
        
        await asyncio.sleep(0.1)  # Esperar un tiempo antes de comprobar nuevamente

def frames_are_similar(frame1, frame2, threshold=30):
    """Compara dos fotogramas para ver si son similares."""
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray1, gray2)
    mean_diff = np.mean(diff)
    return mean_diff < threshold

last_frame = None
threshold = 30  # Umbral para la diferencia entre imágenes

def process_frame(frame):
    global last_frame
    
    if frame is None or frame.size == 0:
        return {"error": "No se pudo cargar el fotograma."}
    
    # Comprobar si este fotograma es similar al anterior
    if last_frame is not None and frames_are_similar(frame, last_frame, threshold):
        return {"message": "El fotograma es similar al anterior, no se procesará."}
    
    last_frame = frame.copy()

    # Realizar la detección de placas
    results_plate = model_plate(frame)
    plates_detected = []

    for result in results_plate:
        boxes = result.boxes  # Coordenadas de las cajas
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            plate_img = frame[y1:y2, x1:x2]

            if plate_img.size == 0:
                continue

            # Realizar la detección de caracteres con el modelo OCR
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
                    "coordinates": [x1, y1, x2, y2]
                })
                detected_plates.append(plate_text.strip())  # Agregar la placa a la lista
                # Validar y registrar la entrada en la base de datos
                validar_y_registrar_entrada(plate_text.strip())

    return {"plates_detected": plates_detected}

def capture_from_camera():
    """Captura fotogramas de la cámara IP y procesa la detección en segundo plano."""
    cap = cv2.VideoCapture(camera_ip_url)

    if not cap.isOpened():
        print("Error al abrir la cámara IP.")
        return {"error": "No se pudo abrir la cámara."}

    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo obtener el fotograma de la cámara.")
            break

        # Procesar el fotograma de la cámara
        result = process_frame(frame)
        print(result)

        # Puedes agregar un pequeño delay o ajustarlo para no capturar fotogramas innecesarios
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

@app.get("/start-camera/")
async def start_camera(background_tasks: BackgroundTasks):
    """Inicia la captura de la cámara IP en segundo plano."""
    background_tasks.add_task(capture_from_camera)
    return {"message": "La captura de la cámara ha comenzado."}

# Si deseas iniciar la aplicación desde el script
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
