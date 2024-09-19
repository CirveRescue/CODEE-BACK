import cv2
from ultralytics import YOLO
import matplotlib.pyplot as plt

# Ruta al archivo del modelo entrenado para detección de placas
model_path_plate = "Models/best.pt"
# Ruta al archivo del modelo entrenado para OCR
model_path_ocr = "Models/best_OCR.pt"

# Cargar los modelos YOLOv8
model_plate = YOLO(model_path_plate)
model_ocr = YOLO(model_path_ocr)

# URL de la cámara IP
camera_ip_url = "rtsp://888888:888888@192.168.5.121:554/cam/realmonitor?channel=1&subtype=0"

# Ruta a una imagen para pruebas
image_path = "images/4.jpg"

# Variable para alternar entre cámara IP y la imagen de pruebaqq
use_camera = False  # Cambiar a True para usar la cámara IP

# Clases de caracteres que el modelo OCR puede detectar
classes_ocr = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 
               'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
def show_image(title, image):
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title(title)
    plt.axis('off')
    plt.show()
    
    
def process_frame(frame):
    if frame is None or frame.size == 0:
        print("Error: No se pudo cargar el fotograma.")
        return

    # Realizar la detección de placas con el primer modelo (detección de placas)
    results_plate = model_plate(frame)

    # Iterar sobre las detecciones de placas
    for result in results_plate:
        boxes = result.boxes  # Coordenadas de las cajas
        for box in boxes:
            # Extraer las coordenadas de la caja
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

            # Recortar la región de la placa
            plate_img = frame[y1:y2, x1:x2]

            if plate_img.size == 0:
                print("Error: No se pudo recortar la placa.")
                continue

            # Mostrar la imagen de la placa detectada (opcional)
            show_image('Placa Detectada', plate_img)

            # Realizar la detección de caracteres con el modelo OCR
            results_ocr = model_ocr(plate_img)

            # Crear una lista para almacenar los caracteres detectados y sus posiciones
            detected_chars = []

            # Iterar sobre las detecciones de caracteres
            for result_ocr in results_ocr:
                boxes_ocr = result_ocr.boxes
                for box_ocr in boxes_ocr:
                    # Obtener la clase detectada (el índice de la clase)
                    cls = int(box_ocr.cls[0])  # Índice de la clase detectada
                    character = classes_ocr[cls]  # Convertir el índice a carácter

                    # Obtener la coordenada X de la caja para ordenar los caracteres
                    x1_char = int(box_ocr.xyxy[0][0])

                    # Almacenar el carácter y su posición X en la lista
                    detected_chars.append((x1_char, character))

            # Ordenar los caracteres por su posición X (de izquierda a derecha)
            detected_chars = sorted(detected_chars, key=lambda x: x[0])

            # Concatenar los caracteres en orden
            plate_text = ''.join([char for _, char in detected_chars])

            # Si se detecta texto, lo mostramos
            if plate_text.strip():
                print(f"Texto detectado: {plate_text.strip()}")

                # Dibujar la caja alrededor de la placa en la imagen original
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, plate_text.strip(), (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            else:
                print("No se detectó texto en la placa.")

    # Mostrar la imagen final con la detección de la placa y los caracteres
    cv2.imshow("Detección de Placas y OCR", frame)

# Si se usa la cámara IP
if use_camera:
    cap = cv2.VideoCapture(camera_ip_url)

    if not cap.isOpened():
        print("Error al abrir la cámara IP.")
        exit()

    while True:
        # Capturar fotograma de la cámara
        ret, frame = cap.read()
        if not ret:
            print("No se pudo obtener el fotograma de la cámara.")
            break

        # Procesar el fotograma de la cámara
        process_frame(frame)

        # Salir si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberar la cámara y cerrar las ventanas
    cap.release()
    cv2.destroyAllWindows()

# Si se usa la imagen de prueba
else:
    # Cargar la imagen de prueba
    frame = cv2.imread(image_path)

    # Procesar la imagen de prueba
    process_frame(frame)

    # Mantener la ventana de la imagen abierta hasta que se presione una tecla
    cv2.waitKey(0)
    cv2.destroyAllWindows()
